# ParkingSmart Architecture

---

## Layers

UI

↓

Services

↓

ALPR Engine

↓

Detector

↓

OCR

↓

Validator

↓

Database

---

## Modules

ui/

تمام صفحات برنامه

---

alpr/

تشخیص پلاک

---

database/

SQLite

---

services/

Business Logic

---

utils/

Helper Functions

---

resources/

Icons

Models

YOLO

OCR

Config

---

## Detection Pipeline

Camera

↓

Frame

↓

Detector

↓

Plate Crop

↓

OCR

↓

Validation

↓

Database

↓

UI

---

## Future

Detector

YOLO11

YOLO12

TensorRT

OpenVINO

OCR

PaddleOCR

EasyOCR

ONNX