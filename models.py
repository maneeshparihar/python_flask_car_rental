from __init__ import db
from datetime import datetime

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    total_stock = db.Column(db.Integer, nullable=False)  # Total number of cars available
    current_stock = db.Column(db.Integer, nullable=False)  # Cars available for rent
    rental_rate_hourly = db.Column(db.Float, nullable=False)
    rental_rate_daily = db.Column(db.Float, nullable=False)
    rental_rate_weekly = db.Column(db.Float, nullable=False)
    availability = db.Column(db.Boolean, default=True)

    def is_available(self):
        """Returns True if at least one car is available for rent"""
        return self.current_stock > 0

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)

class Rental(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    rental_type = db.Column(db.String(10), nullable=False)  # 'hourly', 'daily', 'weekly'
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)  # This will be null until the car is returned
    total_cost = db.Column(db.Float)
    # Define the relationship to the Car model
    car = db.relationship('Car')

    def calculate_cost(self, car):
        """Calculate cost based on rental type and duration."""
        duration = datetime.now() - self.start_time
        if self.rental_type == 'hourly':
            hours = duration.total_seconds() // 3600
            self.total_cost = car.rental_rate_hourly * max(1, hours)
        elif self.rental_type == 'daily':
            days = duration.days
            self.total_cost = car.rental_rate_daily * max(1, days)
        elif self.rental_type == 'weekly':
            weeks = duration.days // 7
            self.total_cost = car.rental_rate_weekly * max(1, weeks)
