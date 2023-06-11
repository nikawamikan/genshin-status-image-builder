from fastapi import FastAPI
import controller.image_controller as image_ctrl
import controller.status_controller as status_ctrl
import controller.util_controller as util_ctrl


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


app.include_router(image_ctrl.router)
app.include_router(status_ctrl.router)
app.include_router(util_ctrl.router)
