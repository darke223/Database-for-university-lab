from app.database import SessionLocal, engine
from app.models.base import Base
from app.models.customer import Customer


def init_db():
    Base.metadata.create_all(bind=engine)


def create_test_customer():
    session = SessionLocal()

    customer = Customer(name="НИИ прочности материалов")

    session.add(customer)
    session.commit()
    session.refresh(customer)

    print(f"Создан заказчик с id = {customer.id_customer}")

    session.close()


if __name__ == "__main__":
    init_db()
    create_test_customer()