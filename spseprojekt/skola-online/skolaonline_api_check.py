from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

import requests


# Hardcoded test settings. Fill these in before running this file.
SKOLAONLINE_BASE_URL = "https://aplikace.skolaonline.cz/solapi/api"
SKOLAONLINE_USERNAME = "Jan Štefánek"
SKOLAONLINE_PASSWORD = "Lupnilak123."
SKOLAONLINE_CLIENT_ID = "test_client"
SKOLAONLINE_SCOPE = "openid offline_access profile sol_api"
REQUEST_TIMEOUT_SECONDS = 20

# Keep this False for a quick login + /v1/user check.
# Set to True if you want the script to try more read endpoints.
RUN_EXTRA_ENDPOINT_EXAMPLES = True


class SkolaOnlineApiError(RuntimeError):
    pass


@dataclass
class SkolaOnlineApiHelper:
    base_url: str
    username: str
    password: str
    client_id: str = SKOLAONLINE_CLIENT_ID
    scope: str = SKOLAONLINE_SCOPE
    timeout_seconds: int = REQUEST_TIMEOUT_SECONDS

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")
        self.session = requests.Session()
        self.access_token: str | None = None
        self.refresh_token: str | None = None

    # // /connect/token
    # // input: grant_type=password, client_id, username, password, scope
    # // output: access_token, refresh_token, expires_in
    # // description: Logs in and stores the bearer access token for later calls.
    def login(self) -> dict[str, Any]:
        token_data = self._post_form(
            "/connect/token",
            data={
                "grant_type": "password",
                "client_id": self.client_id,
                "username": self.username,
                "password": self.password,
                "scope": self.scope,
            },
            message="Login failed",
        )
        self._store_tokens(token_data)
        return token_data

    # // /connect/token
    # // input: grant_type=refresh_token, client_id, refresh_token, optional scope
    # // output: access_token, refresh_token, expires_in
    # // description: Refreshes login without sending username and password again.
    def refresh_access_token(self) -> dict[str, Any]:
        if not self.refresh_token:
            raise SkolaOnlineApiError("No refresh_token stored. Call login() first.")

        token_data = self._post_form(
            "/connect/token",
            data={
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "refresh_token": self.refresh_token,
                "scope": self.scope,
            },
            message="Token refresh failed",
        )
        self._store_tokens(token_data)
        return token_data

    # // /v1/user
    # // input: none
    # // output: personID, userUID, fullName, class.id, class.abbrev, class.name
    # // description: Gets information about the currently logged-in student.
    def get_current_user(self) -> dict[str, Any]:
        return self._get_json("/v1/user", message="Fetching current user failed")

    # // /v1/user/notifications
    # // input: none
    # // output: notifications[] with moduleId and count
    # // description: Gets notification counts for Škola OnLine modules.
    def get_notifications(self) -> dict[str, Any]:
        return self._get_json(
            "/v1/user/notifications",
            message="Fetching notifications failed",
        )

    # // /v1/timeTable
    # // input: StudentId, DateFrom, DateTo
    # // output: days[] with date, schoolYearId, schedules[], subjects, rooms, times
    # // description: Gets the timetable for a student and date range.
    def get_timetable(
        self,
        student_id: str,
        date_from: str,
        date_to: str,
    ) -> dict[str, Any]:
        return self._get_json(
            "/v1/timeTable",
            params={
                "StudentId": student_id,
                "DateFrom": date_from,
                "DateTo": date_to,
            },
            message="Fetching timetable failed",
        )

    # // /v1/timeTable/codeLists
    # // input: studentId
    # // output: semester[] with id, name, dateFrom, dateTo
    # // description: Gets timetable code lists, mainly semesters.
    def get_timetable_code_lists(self, student_id: str) -> dict[str, Any]:
        return self._get_json(
            "/v1/timeTable/codeLists",
            params={"studentId": student_id},
            message="Fetching timetable code lists failed",
        )

    # // /v1/students/{studentId}/marks/list
    # // input: studentId, optional SemesterId, optional SigningFilter=all
    # // output: marks[] and subjects[]
    # // description: Gets a flat list of marks for a student.
    def get_marks_list(
        self,
        student_id: str,
        semester_id: str | None = None,
        signing_filter: str = "all",
    ) -> dict[str, Any]:
        params = {"SigningFilter": signing_filter}
        if semester_id:
            params["SemesterId"] = semester_id

        return self._get_json(
            f"/v1/students/{student_id}/marks/list",
            params=params,
            message="Fetching marks list failed",
        )

    # // /v1/student/marks/{markId}
    # // input: markId, StudentId
    # // output: markText, theme, weight, teacherDisplayName, subjectName
    # // description: Gets detail for one specific mark.
    def get_mark_detail(self, mark_id: str, student_id: str) -> dict[str, Any]:
        return self._get_json(
            f"/v1/student/marks/{mark_id}",
            params={"StudentId": student_id},
            message="Fetching mark detail failed",
        )

    # // /v1/students/{studentId}/marks/bySubject
    # // input: studentId, optional SemesterId
    # // output: subjects[] with marks[]
    # // description: Gets marks grouped by subject.
    def get_marks_by_subject(
        self,
        student_id: str,
        semester_id: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if semester_id:
            params["SemesterId"] = semester_id

        return self._get_json(
            f"/v1/students/{student_id}/marks/bySubject",
            params=params,
            message="Fetching marks by subject failed",
        )

    # // /v1/students/{studentId}/marks/final
    # // input: studentId
    # // output: certificateTerms[] with finalMarks[]
    # // description: Gets final certificate/report-card marks.
    def get_final_marks(self, student_id: str) -> dict[str, Any]:
        return self._get_json(
            f"/v1/students/{student_id}/marks/final",
            message="Fetching final marks failed",
        )

    # // /v1/marks/codeLists
    # // input: StudentId
    # // output: mark-related code lists
    # // description: Gets code lists used by marks endpoints.
    def get_marks_code_lists(self, student_id: str) -> dict[str, Any]:
        return self._get_json(
            "/v1/marks/codeLists",
            params={"StudentId": student_id},
            message="Fetching marks code lists failed",
        )

    # // /v1/messages/received
    # // input: optional Pagination.PageNumber=1, optional Pagination.PageSize=10
    # // output: messages[] with subject, sentDate, text, read, sender
    # // description: Gets received messages.
    def get_received_messages(
        self,
        page_number: int = 1,
        page_size: int = 10,
    ) -> dict[str, Any]:
        return self._get_json(
            "/v1/messages/received",
            params={
                "Pagination.PageNumber": page_number,
                "Pagination.PageSize": page_size,
            },
            message="Fetching received messages failed",
        )

    # // /v1/messages/sent
    # // input: optional Pagination.PageNumber=1, optional Pagination.PageSize=10
    # // output: messages[] with subject, sentDate, text, read, sender
    # // description: Gets sent messages.
    def get_sent_messages(
        self,
        page_number: int = 1,
        page_size: int = 10,
    ) -> dict[str, Any]:
        return self._get_json(
            "/v1/messages/sent",
            params={
                "Pagination.PageNumber": page_number,
                "Pagination.PageSize": page_size,
            },
            message="Fetching sent messages failed",
        )

    # // /v1/students/{studentId}/homeworks
    # // input: studentId, optional Filter=active or all
    # // output: homeworks[] with topic, dateTo, detailedDescription, attachments[]
    # // description: Gets homework assignments for a student.
    def get_homeworks(self, student_id: str, homework_filter: str = "active") -> dict[str, Any]:
        return self._get_json(
            f"/v1/students/{student_id}/homeworks",
            params={"Filter": homework_filter},
            message="Fetching homeworks failed",
        )

    # // /v1/student/homeworks/assignment/attachments/{attachmentId}
    # // input: attachmentId, StudentId
    # // output: binary attachment bytes
    # // description: Downloads a homework attachment.
    def download_homework_attachment(self, attachment_id: str, student_id: str) -> bytes:
        response = self._request(
            "GET",
            f"/v1/student/homeworks/assignment/attachments/{attachment_id}",
            params={"StudentId": student_id},
        )
        if response.ok:
            return response.content

        detail = response.text[:500].replace("\n", " ")
        raise SkolaOnlineApiError(
            f"Downloading homework attachment failed: HTTP {response.status_code}: {detail}"
        )

    # // /v1/students/{studentId}/behaviors
    # // input: studentId, optional RecordsFilter=all
    # // output: behaviors[] with kindOfBehaviorName, date, semesterId
    # // description: Gets behavior notes, praise, and remarks.
    def get_behaviors(
        self,
        student_id: str,
        records_filter: str = "all",
    ) -> dict[str, Any]:
        return self._get_json(
            f"/v1/students/{student_id}/behaviors",
            params={"RecordsFilter": records_filter},
            message="Fetching behaviors failed",
        )

    def _store_tokens(self, token_data: dict[str, Any]) -> None:
        self.access_token = token_data.get("access_token")
        self.refresh_token = token_data.get("refresh_token")
        if not self.access_token:
            raise SkolaOnlineApiError("Token response did not contain access_token")

    def _post_form(
        self,
        path: str,
        data: dict[str, Any],
        message: str,
    ) -> dict[str, Any]:
        response = self.session.post(
            f"{self.base_url}{path}",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=self.timeout_seconds,
        )
        return self._json_or_raise(response, message)

    def _get_json(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        message: str = "Request failed",
    ) -> dict[str, Any]:
        response = self._request("GET", path, params=params)
        return self._json_or_raise(response, message)

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> requests.Response:
        if not self.access_token:
            self.login()

        return self.session.request(
            method,
            f"{self.base_url}{path}",
            params=params,
            headers={"Authorization": f"Bearer {self.access_token}"},
            timeout=self.timeout_seconds,
        )

    @staticmethod
    def _json_or_raise(response: requests.Response, message: str) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError as exc:
            detail = response.text[:500].replace("\n", " ")
            raise SkolaOnlineApiError(
                f"{message}: HTTP {response.status_code}, non-JSON response: {detail}"
            ) from exc

        if response.ok:
            if not isinstance(payload, dict):
                raise SkolaOnlineApiError(f"{message}: expected a JSON object")
            return payload

        raise SkolaOnlineApiError(f"{message}: HTTP {response.status_code}: {payload}")


def main() -> None:
    helper = SkolaOnlineApiHelper(
        base_url=SKOLAONLINE_BASE_URL,
        username=SKOLAONLINE_USERNAME,
        password=SKOLAONLINE_PASSWORD,
    )

    print("Logging in...")
    token_data = helper.login()
    print(f"Login OK. Token expires in: {token_data.get('expires_in')} seconds")

    print("Fetching /v1/user...")
    user = helper.get_current_user()
    student_id = user.get("personID")
    print("API OK.")
    print(f"Name: {user.get('fullName')}")
    print(f"Person ID: {student_id}")

    class_info = user.get("class")
    if isinstance(class_info, dict):
        print(f"Class: {class_info.get('abbrev') or class_info.get('name')}")

    if not RUN_EXTRA_ENDPOINT_EXAMPLES:
        return

    if not isinstance(student_id, str) or not student_id:
        raise SkolaOnlineApiError("Cannot run examples because /v1/user has no personID")

    today = date.today()
    week_later = today + timedelta(days=7)

    examples = {
        "notifications": helper.get_notifications,
        "timetable_code_lists": lambda: helper.get_timetable_code_lists(student_id),
        "marks_list": lambda: helper.get_marks_list(student_id),
        "marks_by_subject": lambda: helper.get_marks_by_subject(student_id),
        "final_marks": lambda: helper.get_final_marks(student_id),
        "marks_code_lists": lambda: helper.get_marks_code_lists(student_id),
        "received_messages": helper.get_received_messages,
        "sent_messages": helper.get_sent_messages,
        "homeworks": lambda: helper.get_homeworks(student_id),
        "behaviors": lambda: helper.get_behaviors(student_id),
        "timetable": lambda: helper.get_timetable(
            student_id,
            f"{today.isoformat()}T00:00:00",
            f"{week_later.isoformat()}T23:59:59",
        ),
    }

    for name, fetch in examples.items():
        try:
            data = fetch()
            print(f"{name}: OK ({len(data)} top-level keys)")
        except SkolaOnlineApiError as exc:
            print(f"{name}: FAILED: {exc}")


if __name__ == "__main__":
    main()
