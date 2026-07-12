# Architecture Decisions (ADR)

## ADR-001

Decision:
Desktop application using PyQt5.

Reason:
Fast development and native Windows support.

---

## ADR-002

Decision:
SQLite database.

Reason:
Simple deployment without database server.

---

## ADR-003

Decision:
Dedicated ALPR module.

Reason:
Separation of UI and recognition engine.

---

## ADR-004

Decision:
YOLO-based detector.

Reason:
High accuracy and future extensibility.

---

## ADR-005

Decision:
PaddleOCR.

Reason:
Good multilingual OCR performance.

---

## ADR-006

Decision:
CPU-first deployment.

Reason:
Target environment is standard parking office PCs.