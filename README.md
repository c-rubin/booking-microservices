# Booking Microservices
<br>

## Requirements

Docker <br><br>


## How to run

Open console at root (this directory) and enter `docker compose up` <br><br>


## Services List
- ### RabbitMQ
  Enables communication between microservices. Visit it at `localhost:15672`.
  
  Default username and password are `guest`.<br><br><br><br><br>

- ### Gateway
  Directs all calls to their respective services. Visit it at `localhost:5000/`.<br><br><br><br><br>
  
- ### Apartments
  Enables adding and removing apartments. Visit it at `localhost:5000/apartments` or `localhost:5001`.
  - `/add` Adds an apartment.
    - Parameters:
      - name (string)
      - address (string)
      - noiselevel (number)
      - floor (number)
     
    - Examples:
      
      `localhost:5000/apartments/add?name=name1&address=address1&noiselevel=1&floor=1`

      `localhost:5001/add?name=name1&address=address1&noiselevel=1&floor=1`<br><br><br>

  - `/remove` Removes an apartment.
    - Parameters:
      - id (string)
     
    - Examples:

      `localhost:5000/apartments/remove?id=d31c8d5a-251d-4a88-bd08-789bf862fe74`

      `localhost:50001/remove?id=d31c8d5a-251d-4a88-bd08-789bf862fe74`<br><br><br>

  - `/list` Lists all existing apartments. Takes no parameters.
 
    - Examples:
   
      `localhost:5000/apartments/list`

      `localhost:5001/list`<br><br><br><br><br>
        
- ### Bookings
  Enables adding, canceling or changing bookings. Visit it at `localhost:5000/bookings` or `localhost:5002`.
  - `/add` Adds a a booking.
    - Parameters:
      - apartment_id (string)
      - from (date string YYYYMMDD)
      - to (date string YYYYMMDD)
      - who (string)
     
    - Examples:
      
      `localhost:5000/bookings/add?apartment_id=d31c8d5a-251d-4a88-bd08-789bf862fe74&from=20201212&to=20211212&who=someone`

      `localhost:5002/add?apartment_id=d31c8d5a-251d-4a88-bd08-789bf862fe74&from=20201212&to=20211212&who=someone`
  <!-- > [!IMPORTANT]
  > Apartment must already exist in order to add a booking!-->
    - `/change` Changes dates of a booking.
 
      - Parameters:
        - id (string)
        - from (date string YYYYMMDD)
        - to (date string YYYYMMDD)
 
      - Examples:
     
        `localhost:5000/bookings/change?id=05b76eeb-9b7f-4c9f-ad16-7e5973e9764f&from=20080101&to=20080131`
  
        `localhost:5002/change?id=05b76eeb-9b7f-4c9f-ad16-7e5973e9764f&from=20080101&to=20080131`<br><br><br>

    - `/cancel` Cancels a booking.
      - Parameters:
        - id (string)
       
      - Examples:
  
        `localhost:5000/bookings/cancelid=05b76eeb-9b7f-4c9f-ad16-7e5973e9764f`
  
        `localhost:5002/cancelid=05b76eeb-9b7f-4c9f-ad16-7e5973e9764f`<br><br><br>

    - `/list` Lists all existing bookings (only id). Takes no parameters.
 
      - Examples:
     
        `localhost:5000/bookings/list`
  
        `localhost:5002/list`<br><br><br>

    - `/listDetail` Lists all existing bookings (all fields). Takes no parameters.
 
      - Examples:
     
        `localhost:5000/bookings/listDetail`
  
        `localhost:5002/listDetail`<br><br><br>

    - `/list` Lists apartments from bookings service (returns same result as /list from apartments service). Takes no parameters.
 
      - Examples:
     
        `localhost:5000/bookings/existing`
  
        `localhost:5002/existing`<br><br><br><br><br>

- ### Search
  Enables searching. Visit it at `localhost:5000/search` or `localhost:5003`.
  - `/search` Searches apartments available for bookings on given time period.
 
    - Parameters
      - from (date string YYYYMMDD)
      - to (date string YYYYMMDD)
     
    - Examples:
     
        `localhost:5000/search/search?from=20221231&to=20230101`
  
        `localhost:5003/search?from=20221231&to=20230101`<br><br><br>

  - `/existingAps` Lists apartments from search service (returns same result as /list from apartments service). Takes no parameters.
 
      - Examples:
     
        `localhost:5000/search/existingAps`
  
        `localhost:5003/existingAps`<br><br><br>

  - `/existingBooks` Lists bookings from search service (returns same result as /list from bookings service). Takes no parameters.
 
      - Examples:
     
        `localhost:5000/search/existingBooks`
  
        `localhost:5003/existingBooks`<br><br><br><br><br>
