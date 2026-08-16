import json
import os
import sys
import unittest
import uuid
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import bcrypt
import requests
from fastapi import UploadFile
from pydantic import ValidationError

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.constant.status_constant import ItemStatusCode
from app.core.config import settings
from app.core.exceptions import BussinessException
from app.db.models.admin_model import Admin
from app.db.models.borrow_record_model import BorrowRecord
from app.db.models.borrow_return_image_model import BorrowReturnImage
from app.db.models.borrow_return_record_model import BorrowReturnRecord
from app.db.models.equipment_model import Equipment
from app.db.models.repair_order_image_model import RepairOrderImage
from app.db.models.repair_order_model import RepairOrder
from app.db.models.repair_report_model import RepairReport
from app.db.models.repair_user_model import RepairUser
from app.db.models.user_model import User
from app.db.session import SessionLocal
from app.schema.borrow_record_schema import BorrowRecordCreate, BorrowRecordCreateOut
from app.schema.admin_borrow_record_schema import BorrowRecordReviewOut
from app.schema.borrow_return_schema import BorrowReturnCreate, BorrowReturnCreateOut
from app.schema.common_schema import LoginIn, RegisterIn
from app.schema.equipment_schema import EquipmentCreate, EquipmentOut
from app.schema.repair_order_schema import (
    RepairOrderActionOut,
    RepairOrderAssignOut,
    RepairOrderCompletionIn,
    RepairOrderCompletionOut,
    RepairOrderOut,
    RepairReportAdminPageOut,
)
from app.schema.repair_report_schema import RepairReportOut


BASE_URL = os.getenv("CAMPUS_TEST_BASE_URL", "http://127.0.0.1:8000")
IMAGE_URL = "https://example.com/test-evidence.png"


def _password_hash(value: str) -> str:
    return bcrypt.hashpw(value.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _assert_result(test_case: unittest.TestCase, response: requests.Response, status: int = 200):
    test_case.assertEqual(response.status_code, status, response.text[:1000])
    payload = response.json()
    test_case.assertIn("code", payload)
    test_case.assertIn("message", payload)
    test_case.assertIn("data", payload)
    return payload


class ApiContractAndFlowTests(unittest.TestCase):
    """HTTP contract, boundary and end-to-end tests against the local service."""

    @classmethod
    def setUpClass(cls):
        cls.session = SessionLocal()
        cls.prefix = f"__api_test_{uuid.uuid4().hex[:10]}"
        cls.password = "TestPass123"
        cls.user = User(
            name="测试学生",
            username=f"{cls.prefix}u",
            password=_password_hash(cls.password),
            image="https://example.com/avatar.png",
        )
        cls.admin = Admin(
            name="测试管理员",
            username=f"{cls.prefix}a",
            password=_password_hash(cls.password),
            image="https://example.com/avatar.png",
        )
        cls.repair_user = RepairUser(
            name="测试维修员",
            username=f"{cls.prefix}r",
            password=_password_hash(cls.password),
            image="https://example.com/avatar.png",
        )
        cls.equipments = [
            Equipment(
                equipment_no=f"{cls.prefix}_{index}",
                equipment_name=f"{cls.prefix}设备{index}",
                status=ItemStatusCode.AVAILABLE,
                is_deleted=0,
            )
            for index in range(1, 4)
        ]
        cls.session.add_all([cls.user, cls.admin, cls.repair_user, *cls.equipments])
        cls.session.commit()
        cls.session.refresh(cls.user)
        cls.session.refresh(cls.admin)
        cls.session.refresh(cls.repair_user)
        for equipment in cls.equipments:
            cls.session.refresh(equipment)
        cls.addClassCleanup(cls._cleanup_database)

        cls.user_token = cls._login("/user/login")
        cls.admin_token = cls._login("/admin/login")
        cls.repair_token = cls._login("/repair/login")

    @classmethod
    def _login(cls, path: str) -> str:
        response = requests.post(
            f"{BASE_URL}{path}",
            json={"username": cls._username_for_path(path), "password": cls.password},
            timeout=10,
        )
        if response.status_code != 200 or response.json().get("code") != 0:
            raise RuntimeError(f"测试账号登录失败：{path} {response.status_code} {response.text}")
        return response.json()["data"]["token"]

    @classmethod
    def _username_for_path(cls, path: str) -> str:
        if path.startswith("/user"):
            return cls.user.username
        if path.startswith("/admin"):
            return cls.admin.username
        return cls.repair_user.username

    @classmethod
    def _cleanup_database(cls):
        session = SessionLocal()
        try:
            user_id = getattr(cls.user, "id", None)
            admin_id = getattr(cls.admin, "id", None)
            repair_user_id = getattr(cls.repair_user, "id", None)
            equipment_ids = [getattr(item, "id", None) for item in cls.equipments]
            borrow_ids = [
                item.id for item in session.query(BorrowRecord).filter(BorrowRecord.user_id == user_id).all()
            ] if user_id else []
            return_records = []
            if borrow_ids:
                return_records = [
                    item.id
                    for item in session.query(BorrowReturnRecord)
                    .filter(BorrowReturnRecord.borrow_record_id.in_(borrow_ids))
                    .all()
                ]
            report_ids = [
                item.id
                for item in session.query(RepairReport).filter(RepairReport.user_id == user_id).all()
            ] if user_id else []
            order_ids = [
                item.id
                for item in session.query(RepairOrder)
                .filter(RepairOrder.repair_report_id.in_(report_ids))
                .all()
            ] if report_ids else []
            if order_ids:
                session.query(RepairOrderImage).filter(RepairOrderImage.repair_order_id.in_(order_ids)).delete(
                    synchronize_session=False
                )
                session.query(RepairOrder).filter(RepairOrder.id.in_(order_ids)).delete(synchronize_session=False)
            if report_ids:
                session.query(RepairReport).filter(RepairReport.id.in_(report_ids)).delete(synchronize_session=False)
            if return_records:
                session.query(BorrowReturnImage).filter(BorrowReturnImage.return_record_id.in_(return_records)).delete(
                    synchronize_session=False
                )
                session.query(BorrowReturnRecord).filter(BorrowReturnRecord.id.in_(return_records)).delete(
                    synchronize_session=False
                )
            if borrow_ids:
                session.query(BorrowRecord).filter(BorrowRecord.id.in_(borrow_ids)).delete(synchronize_session=False)
            if equipment_ids:
                session.query(Equipment).filter(Equipment.id.in_(equipment_ids)).delete(synchronize_session=False)
            if user_id:
                session.query(User).filter(User.id == user_id).delete(synchronize_session=False)
            if admin_id:
                session.query(Admin).filter(Admin.id == admin_id).delete(synchronize_session=False)
            if repair_user_id:
                session.query(RepairUser).filter(RepairUser.id == repair_user_id).delete(synchronize_session=False)
            session.commit()
        finally:
            if hasattr(cls, "session"):
                cls.session.close()
            session.close()

    @staticmethod
    def _headers(token: str | None = None):
        return {"token": token} if token else {}

    def _post_json(self, path: str, token: str, body: dict, expected_status: int = 200):
        response = requests.post(
            f"{BASE_URL}{path}",
            json=body,
            headers=self._headers(token),
            timeout=10,
        )
        return _assert_result(self, response, expected_status)

    def _get(self, path: str, token: str, expected_status: int = 200):
        response = requests.get(
            f"{BASE_URL}{path}",
            headers=self._headers(token),
            timeout=10,
        )
        return _assert_result(self, response, expected_status)

    def _borrow_body(self, equipment_id: int, offset: int = 0):
        start = datetime.now() + timedelta(days=offset + 1)
        return {
            "equipmentId": equipment_id,
            "borrowStartTime": start.strftime("%Y-%m-%d %H:%M:%S"),
            "borrowEndTime": (start + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "purpose": "接口全流程测试",
        }

    def test_openapi_and_auth_contract(self):
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=10)
        spec = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(spec["paths"]), 51)
        for path, operations in spec["paths"].items():
            for method, operation in operations.items():
                if method not in {"get", "post", "put", "patch", "delete"}:
                    continue
                self.assertIn("responses", operation, f"{method} {path}")
                self.assertTrue(operation["responses"], f"{method} {path}")

        payload = self._get("/user/equipment/page", "", 401)
        self.assertEqual(payload["code"], 1)
        wrong_role = self._get("/admin/repair-orders/page", self.user_token, 401)
        self.assertEqual(wrong_role["code"], 1)

    def test_pagination_and_path_boundaries(self):
        for query in ("page=0", "page=-1", "page=10001", "size=0", "size=-1", "size=101"):
            response = requests.get(
                f"{BASE_URL}/user/equipment/page?{query}",
                headers=self._headers(self.user_token),
                timeout=10,
            )
            _assert_result(self, response, 422)
        data = self._get("/user/equipment/page", self.user_token)["data"]
        for field in ("items", "total", "page", "size", "pages"):
            self.assertIn(field, data)
        _assert_result(self, requests.get(
            f"{BASE_URL}/user/equipment/0",
            headers=self._headers(self.user_token),
            timeout=10,
        ), 422)

    def test_all_paginated_endpoint_boundaries(self):
        endpoints = [
            ("/user/equipment/page", self.user_token),
            ("/user/borrow-records/page", self.user_token),
            ("/user/repair-reports/page", self.user_token),
            ("/admin/equipment/page", self.admin_token),
            ("/admin/equipment-category/page", self.admin_token),
            ("/admin/borrow-records/page", self.admin_token),
            ("/admin/repair-reports/page", self.admin_token),
            ("/admin/repair-orders/page", self.admin_token),
            ("/admin/repair-users/page", self.admin_token),
            ("/repair/equipment/page", self.repair_token),
            ("/repair/orders/page", self.repair_token),
        ]
        for path, token in endpoints:
            for query in ("page=0", "size=0", "size=101"):
                with self.subTest(path=path, query=query):
                    response = requests.get(
                        f"{BASE_URL}{path}?{query}",
                        headers=self._headers(token),
                        timeout=10,
                    )
                    _assert_result(self, response, 422)

    def test_all_id_parameter_boundaries(self):
        get_endpoints = [
            ("/user/equipment/0", self.user_token),
            ("/user/borrow-records/0", self.user_token),
            ("/user/repair-reports/0", self.user_token),
            ("/admin/equipment/0", self.admin_token),
            ("/admin/equipment-category/0", self.admin_token),
            ("/admin/borrow-records/0", self.admin_token),
            ("/admin/repair-reports/0", self.admin_token),
            ("/admin/repair-orders/0", self.admin_token),
            ("/repair/equipment/0", self.repair_token),
            ("/repair/orders/0", self.repair_token),
        ]
        for path, token in get_endpoints:
            with self.subTest(method="GET", path=path):
                _assert_result(self, requests.get(
                    f"{BASE_URL}{path}", headers=self._headers(token), timeout=10
                ), 422)

        post_endpoints = [
            ("/user/borrow-records/0/return", self.user_token),
            ("/admin/borrow-records/0/review", self.admin_token),
            ("/admin/repair-reports/0/confirm", self.admin_token),
            ("/admin/repair-orders/0/assign", self.admin_token),
            ("/admin/repair-orders/0/confirm", self.admin_token),
            ("/admin/repair-orders/0/scrap", self.admin_token),
            ("/repair/orders/0/accept", self.repair_token),
            ("/repair/orders/0/start", self.repair_token),
            ("/repair/orders/0/completion", self.repair_token),
        ]
        for path, token in post_endpoints:
            with self.subTest(method="POST", path=path):
                _assert_result(self, requests.post(
                    f"{BASE_URL}{path}", json={}, headers=self._headers(token), timeout=10
                ), 422)
        _assert_result(self, requests.get(
            f"{BASE_URL}/user/equipment/not-a-number",
            headers=self._headers(self.user_token),
            timeout=10,
        ), 422)

    def test_schema_boundaries(self):
        invalid_cases = [
            (RegisterIn, {"username": "abc", "password": "abc123"}),
            (RegisterIn, {"username": "valid_user", "password": "abcdef"}),
            (EquipmentCreate, {"equipmentNo": "", "equipmentName": "x"}),
            (EquipmentCreate, {"equipmentNo": "x", "equipmentName": "x", "price": -1}),
            (BorrowRecordCreate, {"equipmentId": 1, "borrowStartTime": "2026-01-01T10:00:00", "borrowEndTime": "2026-01-01T10:00:00"}),
            (BorrowReturnCreate, {"returnStatus": "normal", "damageDescription": "损坏"}),
            (BorrowReturnCreate, {"returnStatus": "damaged", "damageDescription": "损坏", "damageImages": []}),
            (RepairOrderCompletionIn, {"resultStatus": "unknown", "faultCause": "x", "repairProcess": "x", "repairResult": "x", "beforeImages": [IMAGE_URL], "afterImages": [IMAGE_URL]}),
            (RepairOrderCompletionIn, {"resultStatus": "repaired", "faultCause": "", "repairProcess": "x", "repairResult": "x", "beforeImages": [IMAGE_URL], "afterImages": [IMAGE_URL]}),
            (RepairOrderCompletionIn, {"resultStatus": "repaired", "faultCause": "x", "repairProcess": "x", "repairResult": "x", "beforeImages": [IMAGE_URL] * 10, "afterImages": [IMAGE_URL]}),
        ]
        for model, body in invalid_cases:
            with self.subTest(model=model.__name__, body=body):
                with self.assertRaises((ValidationError, BussinessException)):
                    model.model_validate(body)

    def test_registration_and_equipment_http_boundaries(self):
        for role in ("user", "repair"):
            for body in ({}, {"username": "abc", "password": "abc123"}, {"username": "valid_user", "password": "abcdef"}):
                with self.subTest(role=role, body=body):
                    _assert_result(self, requests.post(
                        f"{BASE_URL}/{role}/register", json=body, timeout=10
                    ), 422)
        _assert_result(self, requests.post(
            f"{BASE_URL}/admin/register",
            json={"username": "abc", "password": "abc123", "registrationCode": "bad"},
            timeout=10,
        ), 422)
        invalid_equipment = [
            {},
            {"equipmentNo": "x", "equipmentName": ""},
            {"equipmentNo": "x" * 61, "equipmentName": "设备"},
            {"equipmentNo": "x", "equipmentName": "设备", "categoryId": 0},
            {"equipmentNo": "x", "equipmentName": "设备", "price": -1},
            {"equipmentNo": "x", "equipmentName": "设备", "status": "unknown"},
        ]
        for body in invalid_equipment:
            with self.subTest(body=body):
                _assert_result(self, requests.post(
                    f"{BASE_URL}/admin/equipment", json=body,
                    headers=self._headers(self.admin_token), timeout=10
                ), 422)

    def test_status_and_length_query_boundaries(self):
        query_endpoints = [
            ("/user/borrow-records/page", self.user_token),
            ("/user/repair-reports/page", self.user_token),
            ("/admin/repair-reports/page", self.admin_token),
            ("/admin/repair-orders/page", self.admin_token),
            ("/repair/orders/page", self.repair_token),
        ]
        for path, token in query_endpoints:
            with self.subTest(path=path, query="status=invalid"):
                _assert_result(self, requests.get(
                    f"{BASE_URL}{path}?status=invalid",
                    headers=self._headers(token), timeout=10
                ), 422)
            with self.subTest(path=path, query="equipmentName=101 chars"):
                _assert_result(self, requests.get(
                    f"{BASE_URL}{path}?equipmentName={'x' * 101}",
                    headers=self._headers(token), timeout=10
                ), 422)

        _assert_result(self, requests.post(
            f"{BASE_URL}/admin/repair-orders/0/assign",
            json={"repairUserId": 1, "assignRemark": "x" * 1001},
            headers=self._headers(self.admin_token), timeout=10
        ), 422)

    def test_upload_size_boundary(self):
        too_large = b"0" * (settings.IMAGE_MAX_SIZE * 1024 * 1024 + 1)
        response = requests.post(
            f"{BASE_URL}/common/upload-image",
            files={"file": ("too-large.png", too_large, "image/png")},
            headers=self._headers(self.user_token),
            timeout=30,
        )
        payload = _assert_result(self, response, 400)
        self.assertNotEqual(payload["code"], 0)

    def test_normal_borrow_and_return_flow(self):
        equipment_id = self.equipments[0].id
        created = self._post_json("/user/borrow-records", self.user_token, self._borrow_body(equipment_id, 0))["data"]
        for field in ("id", "userId", "equipmentId", "borrowStartTime", "borrowEndTime", "purpose", "status", "createTime", "updateTime"):
            self.assertIn(field, created)
        BorrowRecordCreateOut.model_validate(created)
        borrow_id = created["id"]
        self.assertEqual(created["status"], "待审核")
        reviewed = self._post_json(
            f"/admin/borrow-records/{borrow_id}/review",
            self.admin_token,
            {"approved": True, "reviewRemark": "测试通过"},
        )["data"]
        self.assertEqual(reviewed["status"], "已借出")
        BorrowRecordReviewOut.model_validate(reviewed)
        returned = self._post_json(
            f"/user/borrow-records/{borrow_id}/return",
            self.user_token,
            {"returnStatus": "normal", "returnRemark": "设备正常"},
        )["data"]
        for field in ("id", "borrowRecordId", "returnStatus", "returnRemark", "damageDescription", "damageImages", "returnTime", "createTime", "updateTime"):
            self.assertIn(field, returned)
        BorrowReturnCreateOut.model_validate(returned)
        self.assertEqual(returned["returnStatus"], "正常")
        equipment = self._get(f"/user/equipment/{equipment_id}", self.user_token)["data"]
        EquipmentOut.model_validate(equipment)
        self.assertEqual(equipment["status"], "可借用")

    def _create_approved_borrow(self, equipment_id: int, offset: int):
        created = self._post_json("/user/borrow-records", self.user_token, self._borrow_body(equipment_id, offset))["data"]
        self._post_json(
            f"/admin/borrow-records/{created['id']}/review",
            self.admin_token,
            {"approved": True},
        )
        return created["id"]

    def test_damage_repair_and_unrepairable_flows(self):
        borrow_id = self._create_approved_borrow(self.equipments[1].id, 2)
        returned = self._post_json(
            f"/user/borrow-records/{borrow_id}/return",
            self.user_token,
            {"returnStatus": "damaged", "damageDescription": "测试损坏", "damageImages": [IMAGE_URL]},
        )["data"]
        self.assertEqual(returned["returnStatus"], "损坏")

        reports = self._get("/admin/repair-reports/page", self.admin_token)["data"]
        report = next(item for item in reports["items"] if item["equipmentId"] == self.equipments[1].id)
        RepairReportAdminPageOut.model_validate(report)
        report_id = report["id"]
        self.assertEqual(report["status"], "待处理")
        self.assertIsNotNone(report["repairOrderId"])
        order_id = report["repairOrderId"]
        detail = self._get(f"/admin/repair-orders/{order_id}", self.admin_token)["data"]
        RepairOrderOut.model_validate(detail)
        self.assertEqual(detail["status"], "待派单")
        self.assertEqual(detail["damageImages"], [IMAGE_URL])
        self._post_json(f"/admin/repair-reports/{report_id}/confirm", self.admin_token, {})
        assigned = self._post_json(
            f"/admin/repair-orders/{order_id}/assign",
            self.admin_token,
            {"repairUserId": self.repair_user.id, "assignRemark": "请处理"},
        )["data"]
        RepairOrderAssignOut.model_validate(assigned)
        self.assertEqual(assigned["status"], "待接单")
        accepted = self._post_json(f"/repair/orders/{order_id}/accept", self.repair_token, {})["data"]
        RepairOrderActionOut.model_validate(accepted)
        self.assertEqual(accepted["status"], "待维修")
        started = self._post_json(f"/repair/orders/{order_id}/start", self.repair_token, {})["data"]
        RepairOrderActionOut.model_validate(started)
        self.assertEqual(started["status"], "维修中")
        completed = self._post_json(
            f"/repair/orders/{order_id}/completion",
            self.repair_token,
            {
                "resultStatus": "repaired",
                "faultCause": "电源模块故障",
                "repairProcess": "更换模块",
                "repairResult": "恢复正常",
                "beforeImages": [IMAGE_URL],
                "afterImages": [IMAGE_URL],
            },
        )["data"]
        RepairOrderCompletionOut.model_validate(completed)
        self.assertEqual(completed["status"], "待确认")
        self.assertEqual(completed["equipmentStatus"], "已维修")
        confirmed = self._post_json(f"/admin/repair-orders/{order_id}/confirm", self.admin_token, {})["data"]
        RepairOrderActionOut.model_validate(confirmed)
        self.assertEqual(confirmed["status"], "已完成")
        self.assertEqual(confirmed["equipmentStatus"], "可借用")
        student_report = self._get(f"/user/repair-reports/{report_id}", self.user_token)["data"]
        RepairReportOut.model_validate(student_report)
        self.assertEqual(student_report["damageImages"], [IMAGE_URL])
        self.assertEqual(student_report["beforeImages"], [IMAGE_URL])
        self.assertEqual(student_report["afterImages"], [IMAGE_URL])

        unrepairable_borrow = self._create_approved_borrow(self.equipments[2].id, 4)
        self._post_json(
            f"/user/borrow-records/{unrepairable_borrow}/return",
            self.user_token,
            {"returnStatus": "damaged", "damageDescription": "无法修复测试", "damageImages": [IMAGE_URL]},
        )
        reports = self._get("/admin/repair-reports/page", self.admin_token)["data"]["items"]
        unrepairable_report = next(item for item in reports if item["equipmentId"] == self.equipments[2].id)
        unrepairable_order = unrepairable_report["repairOrderId"]
        self._post_json(f"/admin/repair-reports/{unrepairable_report['id']}/confirm", self.admin_token, {})
        self._post_json(
            f"/admin/repair-orders/{unrepairable_order}/assign",
            self.admin_token,
            {"repairUserId": self.repair_user.id},
        )
        self._post_json(f"/repair/orders/{unrepairable_order}/accept", self.repair_token, {})
        self._post_json(f"/repair/orders/{unrepairable_order}/start", self.repair_token, {})
        result = self._post_json(
            f"/repair/orders/{unrepairable_order}/completion",
            self.repair_token,
            {
                "resultStatus": "unrepairable",
                "faultCause": "主板损坏",
                "repairProcess": "检测后无法修复",
                "repairResult": "建议报废",
                "beforeImages": [IMAGE_URL],
                "afterImages": [IMAGE_URL],
            },
        )["data"]
        RepairOrderCompletionOut.model_validate(result)
        self.assertEqual(result["status"], "无法维修")
        self.assertEqual(result["equipmentStatus"], "已损坏")
        scrapped = self._post_json(f"/admin/repair-orders/{unrepairable_order}/scrap", self.admin_token, {})["data"]
        RepairOrderActionOut.model_validate(scrapped)
        self.assertEqual(scrapped["status"], "已报废")
        self.assertEqual(scrapped["equipmentStatus"], "已报废")

    def test_invalid_return_and_repair_requests(self):
        invalid_bodies = [
            {"returnStatus": "invalid"},
            {"returnStatus": "normal", "damageDescription": "不应填写"},
            {"returnStatus": "damaged", "damageDescription": "缺图片", "damageImages": []},
            {"returnStatus": "damaged", "damageDescription": "图片过多", "damageImages": [IMAGE_URL] * 10},
            {"returnStatus": "damaged", "damageDescription": "空图片", "damageImages": [""]},
        ]
        for body in invalid_bodies:
            with self.subTest(body=body):
                response = requests.post(
                    f"{BASE_URL}/user/borrow-records/1/return",
                    json=body,
                    headers=self._headers(self.user_token),
                    timeout=10,
                )
                _assert_result(self, response, 422)

    def test_upload_validation(self):
        response = requests.post(
            f"{BASE_URL}/common/upload-image",
            files={},
            headers=self._headers(self.user_token),
            timeout=10,
        )
        _assert_result(self, response, 422)
        response = requests.post(
            f"{BASE_URL}/common/upload-image",
            files={"file": ("bad.txt", b"not an image", "text/plain")},
            headers=self._headers(self.user_token),
            timeout=10,
        )
        payload = _assert_result(self, response, 400)
        self.assertNotEqual(payload["code"], 0)

    def test_upload_success_contract_without_external_oss(self):
        from app.api.common.common import upload_image

        image = UploadFile(
            file=BytesIO(b"mock-image"),
            filename="ok.png",
            headers={"content-type": "image/png"},
        )
        with patch("app.api.common.common.oss_util.upload_evidence_image", return_value=IMAGE_URL):
            result = upload_image(image)
        payload = result.model_dump()
        self.assertEqual(payload["code"], 0)
        self.assertIsInstance(payload["data"], str)
        self.assertEqual(payload["data"], IMAGE_URL)


def write_report(result: unittest.TestResult):
    failures = result.failures + result.errors
    summary = {
        "baseUrl": BASE_URL,
        "testsRun": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "successful": result.wasSuccessful(),
        "coverage": {
            "openapiPaths": 51,
            "paginatedEndpoints": 11,
            "idPathOperations": 19,
            "repairBranches": ["repaired", "unrepairable"],
            "uploadCases": ["missing", "invalid_extension", "too_large", "success_contract"],
        },
        "failureDetails": [
            {"test": str(test), "traceback": traceback}
            for test, traceback in failures
        ],
    }
    Path("测试结果.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    status = "通过" if result.wasSuccessful() else "存在失败"
    markdown = [
        "# API 测试结果总结",
        "",
        f"- 测试地址：`{BASE_URL}`",
        f"- 测试总数：{result.testsRun}",
        f"- 失败：{len(result.failures)}",
        f"- 错误：{len(result.errors)}",
        f"- 跳过：{len(result.skipped)}",
        f"- 总体结果：**{status}**",
        "",
        "## 覆盖范围",
        "",
        "- OpenAPI 路径：51 条",
        "- 分页接口边界：11 个",
        "- ID 路径操作边界：19 个",
        "- 维修分支：正常修复、无法维修报废",
        "- 上传场景：缺失文件、非法扩展名、超限文件、成功响应契约",
        "",
        "## 说明",
        "",
        "测试使用唯一前缀创建隔离账号、设备及业务记录，并在测试类清理阶段删除。图片业务字段使用固定 URL，上传接口单独验证缺失文件和非法格式。",
    ]
    if failures:
        markdown.extend(["", "## 失败详情", ""])
        for test, traceback in failures:
            markdown.extend([f"### {test}", "", "```text", traceback, "```", ""])
    Path("测试结果总结.md").write_text("\n".join(markdown), encoding="utf-8")


if __name__ == "__main__":
    test_result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(ApiContractAndFlowTests)
    )
    write_report(test_result)
    raise SystemExit(not test_result.wasSuccessful())
