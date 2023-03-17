#!/usr/bin/env python3

'''
ESPP2 web server
'''
# pylint: disable=invalid-name

import logging
from typing import Optional
from os.path import realpath
import uvicorn
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from pydantic import parse_obj_as
from fastapi.staticfiles import StaticFiles
from espp2.main import do_taxes
from espp2.datamodels import ESPPResponse, Wires, Holdings
import json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/files/", response_model=ESPPResponse)
async def create_files(
        transaction_files: list[UploadFile],
        broker: str = Form(...),
        holdfile: UploadFile | None = None,
        wires: str = Form(""),
#        opening_balance: str = Form(...),
        year: int = Form(...)):
    '''File upload endpoint'''
    opening_balance = None
    if wires:
        wires_list = json.loads(wires)
        wires = Wires(wires=wires_list)

    if opening_balance:
        opening_balance = json.loads(opening_balance)
        opening_balance = parse_obj_as(Holdings, opening_balance)

    if holdfile and holdfile.filename == '':
        holdfile = None
    elif holdfile:
        holdfile = holdfile.file
    try:
        report, holdings, summary = do_taxes(
            broker, transaction_files, holdfile, wires, year)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e)) from e
    return ESPPResponse(tax_report=report, holdings=holdings, summary=summary)


app.mount("/", StaticFiles(directory=realpath(
    f'{realpath(__file__)}/../public'), html=True), name='public')

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
