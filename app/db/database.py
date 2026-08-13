from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base, Employer, Job
from app.config.config import DB_URL

engine = create_engine(DB_URL)
conn = engine.connect()

# metadata is a container that holds the table entities and their schemas
# initializes the database
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def seed_database():
    """Idempotently seed the database with sample employers and jobs."""
    if session.query(Employer).first() is not None:
        return

    tech_corp = Employer(
        name="Tech Corp",
        contact_email="hiring@techcorp.com",
        industry="Technology",
    )
    data_inc = Employer(
        name="Data Inc",
        contact_email="jobs@datainc.com",
        industry="Data",
    )
    session.add_all([tech_corp, data_inc])
    session.flush()  # Assigns primary keys so we can link jobs by object.

    session.add_all(
        [
            Job(
                title="Software Engineer",
                description="Builds GraphQL APIs",
                employer=tech_corp,
            ),
            Job(
                title="Data Scientist",
                description="Analyzes data",
                employer=tech_corp,
            ),
            Job(
                title="Product Manager",
                description="Manages product roadmap",
                employer=data_inc,
            ),
        ]
    )
    session.commit()