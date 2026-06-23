from pydantic import BaseModel, Field


class UploadData(BaseModel):
    # Field alias isliye taaki python me file_id rahe, par JSON me fileId ban jaye
    file_id: str = Field(..., alias="fileId")
    filename: str
    status: str
    size_bytes: int  # Size batana hamesha accha hota hai

    class Config:
        populate_by_name = True
