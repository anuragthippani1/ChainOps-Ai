#!/bin/bash
cd backend
python -m uvicorn main:app --port 8000
