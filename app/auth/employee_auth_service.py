from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from database import get_db
from security import SECRET_KEY, ALGORITHM, TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_employee(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    from employees import employee_repository
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        if email is None or role is None:
            raise credentials_exception
        token_data = TokenData(email=email, role=role)
    except (JWTError, ValidationError):
        raise credentials_exception

    emp = employee_repository.get_employee_by_email(db, email=token_data.email)
    if emp is None:
        raise credentials_exception
    return emp

def require_role(required_role_name: str):
    def role_checker(current_employee: dict = Depends(get_current_employee)):
        if not current_employee.role or current_employee.role != required_role_name:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted for this role")
        return current_employee
    return role_checker
