from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
from datetime import datetime
from sqlalchemy import func
from models import db, User, Expense

app = Flask(__name__)
app.config["SECRET_KEY"] = "tu-clave-secreta-super-segura-cambiala-en-produccion"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///expenses.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializar la base de datos
db.init_app(app)

# ==================== DECORADORES ====================


def login_required(f):
    """Decorador para proteger rutas que requieren autenticación"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Por favor inicia sesión primero", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


# ==================== INICIALIZACIÓN DE BASE DE DATOS ====================


def init_db():
    """Crea las tablas y el usuario administrador inicial"""
    with app.app_context():
        db.create_all()

        # Verificar si existe el usuario admin
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            admin = User(username="admin", is_admin=True)
            admin.set_password("admin")
            db.session.add(admin)
            db.session.commit()
            print("✓ Usuario admin creado exitosamente")
        else:
            print("✓ Base de datos inicializada")


# ==================== RUTAS DE AUTENTICACIÓN ====================


@app.route("/login", methods=["GET", "POST"])
def login():
    """Vista de inicio de sesión"""
    # Si ya está logueado, redirigir al index
    if "user_id" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session["user_id"] = user.id
            session["username"] = user.username
            session["is_admin"] = user.is_admin
            flash(f"¡Bienvenido {user.username}!", "success")
            return redirect(url_for("index"))
        else:
            flash("Usuario o contraseña incorrectos", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Cerrar sesión"""
    username = session.get("username", "Usuario")
    session.clear()
    flash(f"Hasta luego {username}!", "info")
    return redirect(url_for("login"))


# ==================== RUTA PRINCIPAL (INDEX/DASHBOARD) ====================


@app.route("/")
@login_required
def index():
    """Dashboard principal con estadísticas"""
    user_id = session.get("user_id")

    # Calcular totales
    total_expenses = (
        db.session.query(func.sum(Expense.amount)).filter_by(user_id=user_id).scalar()
        or 0
    )
    total_debts = (
        db.session.query(func.sum(Expense.amount))
        .filter(Expense.user_id == user_id, Expense.due_date.isnot(None))
        .scalar()
        or 0
    )

    # Contar gastos y deudas
    expenses_count = Expense.query.filter_by(user_id=user_id).count()
    debts_count = Expense.query.filter(
        Expense.user_id == user_id, Expense.due_date.isnot(None)
    ).count()

    # Últimos 5 gastos
    recent_expenses = (
        Expense.query.filter_by(user_id=user_id)
        .order_by(Expense.created_at.desc())
        .limit(5)
        .all()
    )

    # Próximas deudas a vencer (3 más cercanas)
    upcoming_debts = (
        Expense.query.filter(
            Expense.user_id == user_id,
            Expense.due_date.isnot(None),
            Expense.due_date >= datetime.utcnow().date(),
        )
        .order_by(Expense.due_date.asc())
        .limit(3)
        .all()
    )

    return render_template(
        "index.html",
        total_expenses=total_expenses,
        total_debts=total_debts,
        expenses_count=expenses_count,
        debts_count=debts_count,
        recent_expenses=recent_expenses,
        upcoming_debts=upcoming_debts,
    )


# ==================== RUTAS DE EXPENSES ====================


@app.route("/expenses/new", methods=["GET", "POST"])
@login_required
def new_expense():
    """Crear un nuevo gasto"""
    if request.method == "POST":
        try:
            # Obtener datos del formulario
            name = request.form.get("name")
            amount = request.form.get("amount")
            category = request.form.get("category")
            date_str = request.form.get("date")
            due_date_str = request.form.get("due_date")
            element = request.form.get("element")
            comment = request.form.get("comment")

            # Validaciones básicas
            if not name or not amount or not category or not date_str:
                flash("Por favor completa todos los campos obligatorios", "warning")
                return redirect(url_for("new_expense"))

            # Crear el expense
            expense = Expense(
                name=name,
                amount=float(amount),
                category=category,
                date=datetime.strptime(date_str, "%Y-%m-%d").date(),
                element=element if element else None,
                comment=comment if comment else None,
                user_id=session.get("user_id"),
            )

            # Si tiene due_date, es una deuda
            if due_date_str:
                expense.due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()

            db.session.add(expense)
            db.session.commit()
            flash("¡Gasto creado exitosamente!", "success")
            return redirect(url_for("index"))

        except ValueError as e:
            db.session.rollback()
            flash("Error en el formato de los datos. Verifica los campos.", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Error al crear el gasto: {str(e)}", "danger")

    return render_template(
        "new_expense.html", today=datetime.now().strftime("%Y-%m-%d")
    )


@app.route("/expenses")
@login_required
def expenses_list():
    """Lista de todos los gastos"""
    user_id = session.get("user_id")
    expenses = (
        Expense.query.filter_by(user_id=user_id).order_by(Expense.date.desc()).all()
    )

    # Calcular total
    total = sum(e.amount for e in expenses)

    return render_template("expenses.html", expenses=expenses, total=total)


@app.route("/expenses/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_expense(id):
    """Editar un gasto existente"""
    expense = Expense.query.get_or_404(id)

    # Verificar que el expense pertenece al usuario
    if expense.user_id != session.get("user_id"):
        flash("No tienes permiso para editar este gasto", "danger")
        return redirect(url_for("expenses_list"))

    if request.method == "POST":
        try:
            expense.name = request.form.get("name")
            expense.amount = float(request.form.get("amount"))
            expense.category = request.form.get("category")
            expense.date = datetime.strptime(
                request.form.get("date"), "%Y-%m-%d"
            ).date()
            expense.element = request.form.get("element")
            expense.comment = request.form.get("comment")

            due_date_str = request.form.get("due_date")
            if due_date_str:
                expense.due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            else:
                expense.due_date = None

            db.session.commit()
            flash("Gasto actualizado exitosamente!", "success")
            return redirect(url_for("expenses_list"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar: {str(e)}", "danger")

    return render_template("edit_expense.html", expense=expense)


@app.route("/expenses/<int:id>/delete", methods=["POST"])
@login_required
def delete_expense(id):
    """Eliminar un gasto"""
    expense = Expense.query.get_or_404(id)

    # Verificar que el expense pertenece al usuario
    if expense.user_id != session.get("user_id"):
        flash("No tienes permiso para eliminar este gasto", "danger")
        return redirect(url_for("expenses_list"))

    try:
        db.session.delete(expense)
        db.session.commit()
        flash("Gasto eliminado exitosamente", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar: {str(e)}", "danger")

    return redirect(url_for("expenses_list"))


# ==================== RUTAS DE DEUDAS ====================


@app.route("/debts")
@login_required
def debts_list():
    """Lista de deudas (expenses con due_date)"""
    user_id = session.get("user_id")
    debts = (
        Expense.query.filter(Expense.user_id == user_id, Expense.due_date.isnot(None))
        .order_by(Expense.due_date.asc())
        .all()
    )

    # Calcular totales
    total_debts = sum(d.amount for d in debts)
    overdue_debts = [d for d in debts if d.is_overdue]
    total_overdue = sum(d.amount for d in overdue_debts)

    return render_template(
        "debts.html",
        debts=debts,
        total_debts=total_debts,
        overdue_count=len(overdue_debts),
        total_overdue=total_overdue,
    )


# ==================== RUTA DE RESUMEN ====================


@app.route("/summary")
@login_required
def summary():
    """Resumen general de gastos y deudas"""
    user_id = session.get("user_id")

    # Todos los gastos
    all_expenses = (
        Expense.query.filter_by(user_id=user_id).order_by(Expense.date.desc()).all()
    )

    # Separar deudas y gastos pagados
    debts = [e for e in all_expenses if e.is_debt]
    paid_expenses = [e for e in all_expenses if not e.is_debt]

    # Totales por categoría
    categories_data = (
        db.session.query(
            Expense.category,
            func.sum(Expense.amount).label("total"),
            func.count(Expense.id).label("count"),
        )
        .filter_by(user_id=user_id)
        .group_by(Expense.category)
        .all()
    )

    # Gastos por mes (últimos 6 meses)
    monthly_data = (
        db.session.query(
            func.strftime("%Y-%m", Expense.date).label("month"),
            func.sum(Expense.amount).label("total"),
        )
        .filter_by(user_id=user_id)
        .group_by("month")
        .order_by("month")
        .all()
    )

    # Calcular totales generales
    total_paid = sum(e.amount for e in paid_expenses)
    total_debts = sum(d.amount for d in debts)
    grand_total = total_paid + total_debts

    return render_template(
        "summary.html",
        paid_expenses=paid_expenses,
        debts=debts,
        categories=categories_data,
        monthly_data=monthly_data,
        total_paid=total_paid,
        total_debts=total_debts,
        grand_total=grand_total,
    )


# ==================== MANEJO DE ERRORES ====================


@app.errorhandler(404)
def not_found(e):
    """Página no encontrada"""
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(e):
    """Error interno del servidor"""
    db.session.rollback()
    return render_template("500.html"), 500


# ==================== EJECUCIÓN ====================

if __name__ == "__main__":
    init_db()
    print("\n" + "=" * 50)
    print("🚀 Servidor iniciado en http://127.0.0.1:5000")
    print("=" * 50)
    print("📋 Credenciales de acceso:")
    print("   Usuario: admin")
    print("   Contraseña: admin")
    print("=" * 50 + "\n")
    # config for docker
    app.run(host="0.0.0.0", port=5000, debug=True)
