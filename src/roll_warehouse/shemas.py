from pydantic import BaseModel, Field
from datetime import datetime
from fastapi import HTTPException


class MetalRollAdd(BaseModel):
    length: int = Field(..., gt=0)
    weight: int = Field(..., gt=0)


class MetalRoll(MetalRollAdd):
    id: int
    data_add: datetime
    data_del: datetime | None = None


class FilterNums(BaseModel):
    start: int | None
    end: int | None

    def check(self):
        if self.start and self.end and self.start > self.end:
            raise HTTPException(status_code=400, detail='start must be less than end')
        return True


class FilterDates(FilterNums):
    start: datetime | None
    end: datetime | None


class FilterAll(BaseModel):
    id: FilterNums | None
    length: FilterNums | None
    weight: FilterNums | None
    data_add: FilterDates | None
    data_del: FilterDates | None
