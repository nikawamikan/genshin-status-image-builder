from fastapi import FastAPI
import controller.image_controller as image_ctrl
import controller.status_controller as status_ctrl
import controller.util_controller as util_ctrl
import event.dataupdate as dataupdate

dataupdate.json_update_observation_start()


app = FastAPI()


app.include_router(image_ctrl.router)
app.include_router(status_ctrl.router)
app.include_router(util_ctrl.router)
