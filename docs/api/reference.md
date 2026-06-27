# Finanzas Pro API: Referencia Completa

Esta documentación describe todos los endpoints disponibles en el backend de Finanzas Pro, los formatos de petición/respuesta y la lógica de negocio aplicada.

---

## 🔒 Autenticación y Usuarios

### 1. Registro de Usuario
- **Ruta**: `POST /api/v1/auth/register`
- **Rate Limit**: 3 peticiones por minuto.
- **Request Body**:
```json
{
  "username": "usuario_ejemplo",
  "password": "mi_secure_password"
}
```
- **Response**: (Status 201 Created)
```json
{
  "id": 1,
  "username": "usuario_ejemplo",
  "is_active": true,
  "created_at": "2026-06-26T23:00:00Z",
  "updated_at": "2026-06-26T23:00:00Z"
}
```

### 2. Inicio de Sesión
- **Ruta**: `POST /api/v1/auth/login`
- **Rate Limit**: 5 peticiones por minuto.
- **Request (OAuth2 Form-Data)**:
  - `username`: `usuario_ejemplo`
  - `password`: `mi_secure_password`
- **Response**:
```json
{
  "access_token": "ey...",
  "refresh_token": "ey...",
  "token_type": "bearer"
}
```

### 3. Refrescar Token
- **Ruta**: `POST /api/v1/auth/refresh?refresh_token=ey...`
- **Response**: Nuevos tokens de acceso y actualización.

---

## 💳 Cuentas (`/api/v1/accounts`)

### 1. Listar Cuentas
- **Ruta**: `GET /api/v1/accounts`
- **Cabecera**: `Authorization: Bearer <token>`
- **Response**:
```json
[
  {
    "id": 1,
    "user_id": 1,
    "name": "Soles BCP",
    "type": "Ahorros",
    "currency": "Soles",
    "base_balance": 1000.00,
    "real_balance": 1250.00,
    "projected_balance": 1500.00,
    "is_active": true,
    "created_at": "2026-06-26T23:00:00Z",
    "updated_at": "2026-06-26T23:00:00Z"
  }
]
```

### 2. Crear Cuenta
- **Ruta**: `POST /api/v1/accounts`
- **Request Body**:
```json
{
  "name": "Efectivo",
  "type": "Efectivo",
  "currency": "Soles",
  "base_balance": 500.00
}
```

---

## 📊 Dashboard (`/api/v1/dashboard`)

### 1. Resumen de Métricas
- **Ruta**: `GET /api/v1/dashboard?month=6&year=2026`
- **Response**:
```json
{
  "net_worth": 2350.00,
  "cleared_incomes": 1500.00,
  "paid_expenses": 500.00,
  "pending_debt": 650.00,
  "expenses_by_category": {
    "Comida": 200.00,
    "Transporte": 300.00
  },
  "incomes_by_category": {
    "Sueldo": 1500.00
  },
  "accounts_distribution": {
    "Soles BCP": 1250.00,
    "Efectivo": 1100.00
  },
  "debts_by_creditor": {
    "Interbank": 650.00
  },
  "monthly_balance": {
    "incomes": 1500.00,
    "expenses": 500.00
  }
}
```

---

## 💸 Transacciones y Obligaciones

### 1. Ingresos (`/api/v1/incomes`)
- `GET /api/v1/incomes?month=6&year=2026` (Listar ingresos filtrados por mes/año).
- `POST /api/v1/incomes` (Registrar nuevo ingreso. Soporta `goal_id` opcional para sumarse directamente al ahorro acumulado de la meta).

### 2. Gastos (`/api/v1/expenses`)
- `GET /api/v1/expenses?month=6&year=2026`
- `POST /api/v1/expenses`

### 3. Deudas (`/api/v1/debts`)
- `GET /api/v1/debts`
- `POST /api/v1/debts`
- `POST /api/v1/debts/{debt_id}/pay` (Registra un pago de cuota o amortización de capital, descontando el saldo pendiente y generando un `Expense` automático asociado).

### 4. Préstamos (`/api/v1/loans`)
- `GET /api/v1/loans`
- `POST /api/v1/loans` (Crea préstamo, deduciendo saldo con un `Expense` automático).
- `POST /api/v1/loans/{loan_id}/collect` (Registra cobro total o cuota parcial, sumando saldo con un `Income` automático).
