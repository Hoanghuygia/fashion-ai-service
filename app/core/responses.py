from pydantic import BaseModel, ConfigDict, Field


class BaseResponse[DataT](BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    data: DataT | None
    message: str
    stack_trace: str | None = Field(default=None, alias="stackTrace")
    exception_code: str | None = Field(default=None, alias="exceptionCode")


class ErrorResponse(BaseResponse[None]):
    data: None = None


def success_response[DataT](data: DataT, message: str = "OK") -> BaseResponse[DataT]:
    return BaseResponse(data=data, message=message)
