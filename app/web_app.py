import json
import traceback
import logging
from datetime import datetime
from json import JSONDecodeError
from pydantic import ValidationError

from app import InsuranceWorker
from database import Database

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_404_NOT_FOUND
from kafka_logger import KafkaBatchLogger


web_app = FastAPI(dependencies=[Depends(Database.create_tables)])

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger()

kafka_logger = KafkaBatchLogger


@web_app.on_event("shutdown")
async def shutdown_event():
    kafka_logger.close()


@web_app.post("/tariff")
async def adding_tariff(request: Request):
    body: bytes = await request.body()
    body: str = body.decode()

    try:
        body_dict: dict = json.loads(body)
        await InsuranceWorker.adding_tariff(body_dict)
    except JSONDecodeError:
        logger.error(traceback.format_exc())
        return HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="The request body must be in JSON format!"
        )
    except ValidationError as e:
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=e.json()
        )
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

    log = {
        "action": "add_tariff",
        "status": "Success",
        "detail": body_dict,
        "user_ip": request.client.host,
        "time": str(datetime.now())
    }
    kafka_logger.log(log)
    logger.info(log)

    return JSONResponse(
        content={"status": "OK", "msg": "Tariffs added to the database"},
        status_code=HTTP_201_CREATED
    )


@web_app.get("/calculate_insurance")
async def calculate_insurance(request: Request, cargo_type: str, date: datetime, cost: float):
    try:
        price = await InsuranceWorker.calculate_insurance(cargo_type, date, cost)
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

    if price is None:
        log = {
            "action": "calculate_insurance",
            "status": "Fail",
            "detail": f"cargo_type: {cargo_type}, date: {date}, cost: {cost}",
            "user_ip": request.client.host,
            "time": str(datetime.now())
        }
        print("before kafka log")
        kafka_logger.log(log)
        logger.info(log)
        return JSONResponse(
            {"status": "ERROR", "result": "Tariff not found. Cargo type or date not valid!"},
            status_code=HTTP_404_NOT_FOUND
        )

    log = {
        "action": "calculate_insurance",
        "status": "Success",
        "detail": f"cargo_type: {cargo_type}, date: {date}, cost: {cost}, price: {price}",
        "user_ip": request.client.host,
        "time": str(datetime.now())
    }
    kafka_logger.log(log)
    logger.info(log)

    return JSONResponse({"status": "OK", "result": price})


@web_app.delete("/tariff")
async def delete_tariff(request: Request, cargo_type: str, date: datetime):
    result = await InsuranceWorker.delete_tariff(cargo_type, date)
    if not result:
        log = {
            "action": "delete_tariff",
            "status": "Fail",
            "detail": f"cargo_type: {cargo_type}, date: {date}",
            "user_ip": request.client.host,
            "time": str(datetime.now())
        }
        kafka_logger.log(log)
        logger.info(log)
        return JSONResponse(
            {"msg": "Tariff not found. Cargo type or date not valid!"},
            status_code=HTTP_404_NOT_FOUND
        )

    log = {
        "action": "delete_tariff",
        "status": "Success",
        "detail": f"cargo_type: {cargo_type}, date: {date}",
        "user_ip": request.client.host,
        "time": str(datetime.now())
    }
    kafka_logger.log(log)
    logger.info(log)

    return JSONResponse({"msg": "Tariff deleted"})


@web_app.put("/tariff")
async def update_tariff(request: Request, cargo_type: str, date: datetime, new_rate: float):
    result = await InsuranceWorker.update_tariff(cargo_type, date, new_rate)
    if not result:
        log = {
            "action": "update_tariff",
            "status": "Fail",
            "detail": f"cargo_type: {cargo_type}, date: {date}",
            "user_ip": request.client.host,
            "time": str(datetime.now())
        }
        logger.info(log)
        kafka_logger.log(log)

        return JSONResponse(
            {"msg": "Tariff not found. Cargo type or date not valid!"},
            status_code=HTTP_404_NOT_FOUND
        )

    log = {
        "action": "update_tariff",
        "status": "Success",
        "detail": f"cargo_type:{cargo_type}, date: {date}, new_rate: {new_rate}",
        "user_ip": request.client.host,
        "time": str(datetime.now())
    }
    kafka_logger.log(log)
    logger.info(f"Tariff updated. Details: cargo_type:{cargo_type}, date: {date}, new_rate: {new_rate}")

    return JSONResponse(
        {"msg": "Tariff updated"}
    )
