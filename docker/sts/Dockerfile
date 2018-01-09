# Clone FranhoferIOSB SensorThingsServer from github
FROM alpine/git as clone
WORKDIR /app
RUN git clone https://github.com/FraunhoferIOSB/SensorThingsServer.git

# Copy java sources to /app/SensorThings/Server directory and build the project with Maven
FROM maven:3.5-jdk-8-alpine as build
WORKDIR /app
COPY --from=clone /app/SensorThingsServer /app
RUN mvn -Dmaven.test.skip=true -Dmaven.javadoc.skip=true install

# Copy the built war file and our settins to Tomcat and run Tomcat
FROM tomcat:8-jre8-alpine

EXPOSE 8080
EXPOSE 11883

ADD http://repo.maven.apache.org/maven2/org/postgresql/postgresql/9.4.1212/postgresql-9.4.1212.jar /usr/local/tomcat/lib/
ADD http://repo.maven.apache.org/maven2/net/postgis/postgis-jdbc/2.2.1/postgis-jdbc-2.2.1.jar /usr/local/tomcat/lib/

COPY --from=build /app/SensorThingsServer/target/SensorThingsServer-1.3-SNAPSHOT.war /usr/local/tomcat/webapps/SensorThingsService.war
COPY ./SensorThingsService.xml /usr/local/tomcat/conf/Catalina/localhost/SensorThingsService.xml
