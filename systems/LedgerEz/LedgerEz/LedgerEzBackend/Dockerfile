# --- STAGE 1: The "Build" Stage ---
# We use a specific Java 21 + Maven image to build our app
FROM maven:3.9-eclipse-temurin-21 AS builder

# Set the working directory inside the container
WORKDIR /app

# Copy the pom.xml first. This is a Docker cache optimization.
# If pom.xml doesn't change, Docker reuses the downloaded dependencies.
COPY pom.xml .
RUN mvn dependency:go-offline

# Copy the rest of the source code
COPY src ./src

# Build the application, creating the executable .jar file.
# We skip tests here, assuming they're run in a separate CI step.
RUN mvn package -DskipTests

# --- STAGE 2: The "Run" Stage ---
# We use a JRE-only, slim, Alpine Linux image. It's tiny and secure.
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

# Copy *only* the built .jar file from the 'builder' stage
COPY --from=builder /app/target/*.jar app.jar

# Expose port 9000 (the port our Spring app runs on, see application.properties)
EXPOSE 9000

# This is the command that will run when the container starts
# It's the same as 'java -jar app.jar'
ENTRYPOINT ["java", "-jar", "app.jar"]