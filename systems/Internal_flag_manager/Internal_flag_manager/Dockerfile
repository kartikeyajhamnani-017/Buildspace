# --- STAGE 1: The "Build" Stage ---
FROM maven:3.9-eclipse-temurin-21 AS builder

WORKDIR /app

# Copy the pom.xml first. This is a Docker cache optimization.
# If pom.xml doesn't change, Docker reuses the downloaded dependencies.
COPY pom.xml .
RUN mvn dependency:go-offline

# Copy the rest of the source code
COPY src ./src

# Build the application, creating the executable .jar file.
RUN mvn package -DskipTests

# --- STAGE 2: The "Run" Stage ---
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

# Copy *only* the built .jar file from the 'builder' stage
COPY --from=builder /app/target/*.jar app.jar

# Expose the port your Spring app runs on (see application.properties)
EXPOSE 8000

CMD ["java", "-jar", "app.jar"]
