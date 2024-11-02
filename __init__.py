from flask import Flask, render_template, redirect, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from config import Config 
import json
# from models import Car, Customer, Rental 

db = SQLAlchemy()

def create_app():
  app = Flask(__name__)
  app.config.from_object(Config)
  db.init_app(app)
  
  def add_sample_cars():
    cars = [
        Car(make='Toyota', model='Camry', year=2020, total_stock=5, current_stock =5, availability=True, rental_rate_hourly=10.0, rental_rate_daily=60.0, rental_rate_weekly=400.0),
        Car(make='Honda', model='Accord', year=2021, total_stock=5, current_stock =5, availability=True, rental_rate_hourly=12.0, rental_rate_daily=70.0, rental_rate_weekly=450.0),
        Car(make='Tesla', model='Model 3', year=2022, total_stock=5, current_stock =5, availability=True, rental_rate_hourly=20.0, rental_rate_daily=120.0, rental_rate_weekly=800.0),
        Car(make='Ford', model='Mustang', year=2019, total_stock=5, current_stock =5, availability=True, rental_rate_hourly=15.0, rental_rate_daily=90.0, rental_rate_weekly=600.0),
        Car(make='BMW', model='3 Series', year=2021, total_stock=5, current_stock =5, availability=True, rental_rate_hourly=25.0, rental_rate_daily=150.0, rental_rate_weekly=1000.0),
    ]
    # Add cars to session
    db.session.bulk_save_objects(cars)
    db.session.commit()
  
  
  with app.app_context():
    from models import Car, Customer, Rental 
    db.create_all()
    reset_database = False # Set to True to reset the database. Set to False to keep the database.
    if reset_database:
        db.session.query(Car).delete()
        db.session.query(Customer).delete()
        db.session.query(Rental).delete()
        db.session.commit() 
        add_sample_cars() 
  
  @app.route('/', methods=['GET', 'POST'])
  def home():
      if request.method == "POST":
        email = request.form.get('email')
        name = request.form.get('name')
        phone = request.form.get('phone')
        return redirect(url_for('view_cars', email=email, name=name, phone=phone))
      return render_template('home.html')
  
  @app.route('/cars', methods=['GET', 'POST'])
  def view_cars():
      if request.method == 'GET':
          # Retrieve customer details from the query parameters
          email = request.args.get('email')
          name = request.args.get('name')
          phone = request.args.get('phone')

          # Get the customer information
          customer = Customer.query.filter_by(email=email).first()
          if not customer:
              customer = Customer(email=email, name=name, phone=phone)
              db.session.add(customer)
              db.session.commit()
          print(vars(customer))
          # Get cars available for rent
          available_cars = Car.query.filter(Car.current_stock > 0).all()
          print(available_cars)
          # Get the cars that the customer has rented
          rented_cars = Rental.query.filter_by(customer_id=customer.id, end_time=None).all()
          historical_rented_cars = Rental.query.filter(Rental.customer_id == customer.id, Rental.end_time != None).all()
          print(rented_cars)
          return render_template('cars.html', available_cars=available_cars, rented_cars=rented_cars,  historical_rented_cars=historical_rented_cars, email=email, name=name, phone=phone)

      elif request.method == 'POST':
          # Retrieve customer and rental information from form data
          email = request.form.get('email')
          name = request.form.get('name')
          phone = request.form.get('phone')
          car_id = request.form.get('car_id')
          rental_type = request.form.get('rental_type')

          customer = Customer.query.filter_by(email=email).first()
        #   if not customer:
        #       customer = Customer(email=email, name=name, phone=phone)
        #       db.session.add(customer)
        #       db.session.commit()

          car = Car.query.get(car_id)
          if car.is_available():
              # Create a new rental
              rental = Rental(
                  customer_id=customer.id,
                  car_id=car_id,
                  rental_type=rental_type,
                  start_time=datetime.now(),
              )
              db.session.add(rental)

              # Reduce the available stock of the car
              car.current_stock -= 1

              db.session.commit()

              flash('Car rented successfully!')
          else:
              flash('The selected car is no longer available for rent.')

          return redirect(url_for('view_cars', email=email, name=name, phone=phone))
      
    # return render_template('cars.html', cars=cars, email=email, name=name, phone=phone)
    
  @app.route('/return/<int:rental_id>', methods=['POST'])
  def return_car(rental_id):
      rental = Rental.query.get(rental_id)
      customer = Customer.query.get(rental.customer_id)
      print("customer is ", customer)
      if rental and rental.end_time is None:
          rental.end_time = datetime.now()
          
          # Fetch the car and calculate the total cost
          car = Car.query.get(rental.car_id)
          rental.calculate_cost(car)

          # Increase the car's current stock
          car.current_stock += 1

          db.session.commit()

          flash(f'Car returned! Total cost: ${rental.total_cost:.2f}')
      else:
          flash('Unable to return the car. Please try again.')

      return redirect(url_for('view_cars', email=customer.email))
  
  return app
