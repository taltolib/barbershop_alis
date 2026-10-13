from fastapi import HTTPException


class Err:
    SESSION_INVALID = 1001      # просрочена, неверна или не передана
    ACCOUNT_DISABLED = 1002     # барбер уволен
    FORBIDDEN = 1003            # нет прав на действие
    BAD_CREDENTIALS = 1004      # неверный логин или пароль
    USERNAME_TAKEN = 1005       # логин уже занят
    USER_NOT_FOUND = 1006      # пользователь не найден
    ALREADY_DISMISSED = 1007   # барбер уже уволен


def api_error(status: int, code: int, message: str) -> HTTPException:
    return HTTPException(status, detail={"code": code, "message": message})