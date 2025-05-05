# Hermit - CPSC 362 Final Project

Hermit is a web-based property management platform designed to simplify the experience of searching, booking, and listing rental properties.

Hermit provides services to potential tenants and property owners by incorporating the process of discovering and exploring properties in a collectively, intuitive interface.

Hermit's design is ideal for potential tenants and property owners. It serves as a powerful tool for the purpose of finding a property that fits everyone's needs. 

### Vision Statement:
Inspired by the adaptability of the hermit crab, Hermit provides a reliable platform for travelers to discover and book unique accommodations worldwide. Whether seeking a peaceful retreat, an urban escape, or a short term residence, guests can connect with trusted hosts offering well described spaces. With intelligent search, secure transactions, and a commitment to quality, Hermit ensures a smooth and dependable experience for every stay.


## Features
- User Account: Secure account sign ups and logins for convenient usage.

- Property Listings: List property by location, price range, and visual photos.

- Search Listings: Find property listings by location, price range, and booking availability.

- Visualized Listings: View detailed photos of the property, accurately representing the listing.

- Responsive & User Friendly Design: Web design is simple, effective, and easy to navigate, accounting for new users.

- Secure Payment & Privacy: Utilizes a secure and safe methods of payment and account management. Built to focus on data security and user privacy.

### Functional Requirements

1. User Registration - Register account and verify user's identity.

2. Property Listing & Management - Allow users (house owners) to upload their house image and describe their housing condition.

3. Search & Booking System - Users can search by filter and book their reservation.

4. Payment - User can proceed to payment.

5. Review - Allow both user and house owner to leave a review after their stay.

### Non-functional Requirements

1. Security - secure payment processing.

2. Performance and accuracy - Search result and navigation between the site should be under 3 seconds.

3. Easy UI - User interface should be clean, interactive links should be at least 2 centimeters.

4. Accessibility - Desktop website and phone website should show the same result.

5. Scalability - Accomodate large user traffic.

### Diagram

![Hermit](https://github.com/user-attachments/assets/63e3fac6-d8c0-4c1a-86b1-4b64129ccd05)

## Setup
To get the Hermit app up and running on your local machine:

### 1. Clone the Github repository
- git clone https://github.com/martintran23/hermit2.git

### 2. Install Git Bash (optional)
- Download here: https://git-scm.com/downloads

### 3. Open project folder in terminal or in Git Bash
- If using terminal: cd hermit2
- If using Git Bash: Manually open project folder with Git Bash

### 4. Install dependencies
- pip install flask
- pip install -r requirements.txt

### 5. Install MongoDB
- https://www.mongodb.com/try/download/community
- Connect to localhost:27017
1. docker ps -a
2. docker start hermit-mongo
3. (skip to step 4 if docker running on correct address):
docker run -d \
  --name hermit-mongo \
  -p 27017:27017 \
  mongo:6.0
4. docker exec hermit-mongo mongosh --eval "db.runCommand({ ping: 1 })"
5. if terminal responds with { "ok" : 1 } then you are succesfully connected to mongodb://localhost:27017

### 6. Run virtual enviroment
- source venv/bin/activate

### 7. Run Flask server
- python -m server.app

### 8. Run Website
- Web Browser: http://localhost:5000/
- Or open forwarded port link (ex.https://8q42kvkd-5000.usw3.devtunnels.ms/)