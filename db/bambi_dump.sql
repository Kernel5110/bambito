-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: bambidb
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `almacen`
--

DROP TABLE IF EXISTS `almacen`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `almacen` (
  `ID_Almacen` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(50) NOT NULL,
  `Ubicacion` varchar(100) NOT NULL,
  `Capacidad` int NOT NULL,
  `Estado` varchar(20) NOT NULL DEFAULT 'Activo',
  PRIMARY KEY (`ID_Almacen`),
  UNIQUE KEY `Nombre` (`Nombre`),
  CONSTRAINT `almacen_chk_1` CHECK ((`Capacidad` > 0)),
  CONSTRAINT `almacen_chk_2` CHECK ((`Estado` in (_utf8mb4'Activo',_utf8mb4'Inactivo',_utf8mb4'Mantenimiento')))
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `almacen`
--

LOCK TABLES `almacen` WRITE;
/*!40000 ALTER TABLE `almacen` DISABLE KEYS */;
INSERT INTO `almacen` VALUES (1,'Almacén Principal','Calle 123, CDMX',1000,'Activo'),(2,'Almacén Secundario','Av. Viva 456, CDMX',500,'Activo'),(3,'Almacén Temporal','Calle 789, CDMX',300,'Mantenimiento'),(4,'Almacén Nuevo','Principal 321, CDMX',700,'Inactivo'),(5,'Almacén Central','Calle 456, CDMX',800,'Activo'),(6,'Almacén Regional','Av. Viva 654, CDMX',600,'Activo');
/*!40000 ALTER TABLE `almacen` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `almacen_insumo`
--

DROP TABLE IF EXISTS `almacen_insumo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `almacen_insumo` (
  `FK_ID_Almacen` int NOT NULL,
  `FK_ID_Insumo` int NOT NULL,
  `Unidades` int NOT NULL,
  `Fecha_Actualizacion` date NOT NULL DEFAULT (curdate()),
  `Minimo_Stock` int NOT NULL,
  PRIMARY KEY (`FK_ID_Almacen`,`FK_ID_Insumo`),
  KEY `FK_ID_Insumo` (`FK_ID_Insumo`),
  CONSTRAINT `almacen_insumo_ibfk_1` FOREIGN KEY (`FK_ID_Almacen`) REFERENCES `almacen` (`ID_Almacen`) ON DELETE CASCADE,
  CONSTRAINT `almacen_insumo_ibfk_2` FOREIGN KEY (`FK_ID_Insumo`) REFERENCES `insumo` (`ID_Insumo`) ON DELETE CASCADE,
  CONSTRAINT `almacen_insumo_chk_1` CHECK ((`Unidades` >= 0)),
  CONSTRAINT `almacen_insumo_chk_2` CHECK ((`Minimo_Stock` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `almacen_insumo`
--

LOCK TABLES `almacen_insumo` WRITE;
/*!40000 ALTER TABLE `almacen_insumo` DISABLE KEYS */;
INSERT INTO `almacen_insumo` VALUES (1,1,50,'2023-01-01',10),(2,2,30,'2023-01-02',5),(3,3,100,'2023-01-03',20),(4,4,150,'2023-01-04',30),(5,5,200,'2023-01-05',40),(6,6,50,'2023-01-06',10);
/*!40000 ALTER TABLE `almacen_insumo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `almacen_materiaprima`
--

DROP TABLE IF EXISTS `almacen_materiaprima`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `almacen_materiaprima` (
  `FK_ID_Almacen` int NOT NULL,
  `FK_ID_MateriaPrima` int NOT NULL,
  `Unidades` int NOT NULL,
  `FechaVencimiento` date NOT NULL,
  `Lote` varchar(50) NOT NULL,
  `Minimo_Stock` int NOT NULL,
  PRIMARY KEY (`FK_ID_Almacen`,`FK_ID_MateriaPrima`),
  KEY `FK_ID_MateriaPrima` (`FK_ID_MateriaPrima`),
  CONSTRAINT `almacen_materiaprima_ibfk_1` FOREIGN KEY (`FK_ID_Almacen`) REFERENCES `almacen` (`ID_Almacen`) ON DELETE CASCADE,
  CONSTRAINT `almacen_materiaprima_ibfk_2` FOREIGN KEY (`FK_ID_MateriaPrima`) REFERENCES `materiaprima` (`ID_MateriaPrima`) ON DELETE CASCADE,
  CONSTRAINT `almacen_materiaprima_chk_1` CHECK ((`Unidades` >= 0)),
  CONSTRAINT `almacen_materiaprima_chk_2` CHECK ((`Minimo_Stock` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `almacen_materiaprima`
--

LOCK TABLES `almacen_materiaprima` WRITE;
/*!40000 ALTER TABLE `almacen_materiaprima` DISABLE KEYS */;
INSERT INTO `almacen_materiaprima` VALUES (1,1,100,'2023-12-31','Lote001',20),(2,2,200,'2023-12-31','Lote002',30),(3,3,300,'2023-12-31','Lote003',40),(4,4,50,'2023-12-31','Lote004',10),(5,5,500,'2023-12-31','Lote005',50),(6,6,1000,'2023-12-31','Lote006',100);
/*!40000 ALTER TABLE `almacen_materiaprima` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `catproducto`
--

DROP TABLE IF EXISTS `catproducto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `catproducto` (
  `ID_CatProducto` int NOT NULL AUTO_INCREMENT,
  `Nombre_prod` varchar(100) NOT NULL,
  `Descripcion` text,
  `Precio` decimal(10,2) NOT NULL,
  `Stock` int NOT NULL DEFAULT '0',
  `Imagen` varchar(255) DEFAULT NULL,
  `Caducidad` date NOT NULL,
  `Sabor` varchar(50) DEFAULT NULL,
  `IVA` decimal(4,2) NOT NULL DEFAULT '0.16',
  `Estado` varchar(20) NOT NULL DEFAULT 'Disponible',
  `FK_ID_SubtipoProducto` int NOT NULL,
  `FK_ID_Receta` int NOT NULL,
  PRIMARY KEY (`ID_CatProducto`),
  UNIQUE KEY `Nombre_prod` (`Nombre_prod`),
  KEY `FK_ID_SubtipoProducto` (`FK_ID_SubtipoProducto`),
  KEY `FK_ID_Receta` (`FK_ID_Receta`),
  CONSTRAINT `catproducto_ibfk_1` FOREIGN KEY (`FK_ID_SubtipoProducto`) REFERENCES `subtipoproducto` (`ID_SubtipoProducto`),
  CONSTRAINT `catproducto_ibfk_2` FOREIGN KEY (`FK_ID_Receta`) REFERENCES `receta` (`ID_Receta`),
  CONSTRAINT `catproducto_chk_1` CHECK ((`Precio` > 0)),
  CONSTRAINT `catproducto_chk_2` CHECK ((`Stock` >= 0)),
  CONSTRAINT `catproducto_chk_3` CHECK ((`IVA` >= 0)),
  CONSTRAINT `catproducto_chk_4` CHECK ((`Estado` in (_utf8mb4'Disponible',_utf8mb4'Agotado',_utf8mb4'Descontinuado')))
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `catproducto`
--

LOCK TABLES `catproducto` WRITE;
/*!40000 ALTER TABLE `catproducto` DISABLE KEYS */;
INSERT INTO `catproducto` VALUES (7,'Concha de vainilla','Pan dulce tradicional con cobertura de vainilla',10.00,50,'imagenes/panes/concha.png','2025-12-31','Vainilla',0.16,'Disponible',1,1),(8,'Baguette rústica','Pan salado ideal para sándwiches',15.00,40,'imagenes/panes/baguette.png','2025-10-15',NULL,0.16,'Disponible',2,4),(9,'Pastel cumple Choco','Pastel de chocolate con velitas',250.00,9,'imagenes/panes/pastel_choco.png','2025-09-01','Chocolate',0.16,'Disponible',3,2),(10,'Pastel boda 3 pisos','Decorado con flores blancas',800.00,2,'imagenes/panes/pastel_boda.png','2025-12-25','Fresa',0.16,'Disponible',4,5),(11,'Galleta choco chip','Crujiente y dulce',5.00,97,'imagenes/panes/galleta_chocolate.png','2025-08-20','Chocolate',0.16,'Disponible',5,3),(12,'Galleta avena','Galletas saludables con avena y pasas',6.50,71,'imagenes/panes/avena.png','2025-08-22','Avena',0.16,'Disponible',6,6),(25,'Pan Francés','Pan tradicional francés',15.00,100,'imagenes/panes/pan_frances.png','2023-12-31','Salado',0.16,'Disponible',1,1),(26,'Pastel de vainilla','Pastel de chocolate con cobertura',150.00,50,'imagenes/panes/pastel_vainilla.png','2023-12-31','Chocolate',0.16,'Disponible',2,2),(33,'Bigote','Pan dulce en forma de bigote',8.00,16,'imagenes/panes/bigote.png','2025-05-10','vainilla',0.16,'Disponible',0,0),(34,'Bisquet','Pan suave tipo bisquet',9.00,20,'imagenes/panes/bisquet.png','2025-05-10','natural',0.16,'Disponible',0,0),(35,'Bolillo','Pan salado para acompañar comidas',2.50,5,'imagenes/panes/bolillo.png','2025-05-08','salado',0.16,'Disponible',0,0),(36,'Concha','Pan dulce con cubierta azucarada',7.00,10,'imagenes/panes/concha.png','2025-05-09','chocolate',0.16,'Disponible',0,0),(37,'Croissant','Pan de hojaldre tipo francés',12.00,20,'imagenes/panes/croissant.png','2025-05-09','mantequilla',0.16,'Disponible',0,0),(38,'Cuernito','Pan con forma de cuerno',6.00,12,'imagenes/panes/cuernito.png','2025-05-10','vainilla',0.16,'Disponible',0,0),(39,'Cupcake','Pastelito individual decorado',10.00,15,'imagenes/panes/cupcake.png','2025-05-12','fresa',0.16,'Disponible',0,0),(40,'Dona','Pan frito con glaseado',8.50,15,'imagenes/panes/dona.png','2025-05-11','azúcar',0.16,'Disponible',0,0),(41,'EmpanadaPina','Empanada rellena de piña',7.50,10,'imagenes/panes/empanada_pina.png','2025-05-10','piña',0.16,'Disponible',0,0),(42,'Focaccia','Pan italiano con hierbas',15.00,8,'imagenes/panes/focaccia.jpg','2025-05-12','romero',0.16,'Disponible',0,0),(43,'Galleta_Chocolate','Galleta con trozos de chocolate',5.00,20,'imagenes/panes/galleta_chocolate.jpg','2025-06-01','chocolate',0.16,'Disponible',0,0),(44,'Oreja','Pan de hojaldre con azúcar',6.00,14,'imagenes/panes/oreja.jpg','2025-05-10','azúcar',0.16,'Disponible',0,0),(45,'PanHamburguesa','Pan redondo para hamburguesas',4.00,12,'imagenes/panes/panhamburguesa.jpg','2025-05-09','natural',0.16,'Disponible',0,0),(46,'Polvoron','Pan seco que se deshace en la boca',3.50,10,'imagenes/panes/polvoron.jpg','2025-06-01','vainilla',0.16,'Disponible',0,0),(47,'Telera','Pan tradicional mexicano',3.00,10,'imagenes/panes/telera.jpg','2025-05-09','salado',0.16,'Disponible',0,0);
/*!40000 ALTER TABLE `catproducto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cliente`
--

DROP TABLE IF EXISTS `cliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cliente` (
  `Id_Cliente` int NOT NULL AUTO_INCREMENT,
  `Nombre_Cliente_cliente` varchar(50) NOT NULL,
  `Ap_Paterno_cliente_cli` varchar(50) NOT NULL,
  `Ap_Materno_cleinte_cli` varchar(50) NOT NULL,
  `Telefono_cli` bigint NOT NULL,
  `Correo` varchar(100) DEFAULT NULL,
  `RFC` varchar(13) DEFAULT NULL,
  `Calle` varchar(100) NOT NULL,
  `Colonia` varchar(100) NOT NULL,
  `Cod_Postal` int NOT NULL,
  `Fecha_Registro` date NOT NULL DEFAULT (curdate()),
  `Estado` varchar(20) NOT NULL DEFAULT 'Activo',
  PRIMARY KEY (`Id_Cliente`),
  CONSTRAINT `cliente_chk_1` CHECK ((`Estado` in (_utf8mb4'Activo',_utf8mb4'Inactivo')))
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cliente`
--

LOCK TABLES `cliente` WRITE;
/*!40000 ALTER TABLE `cliente` DISABLE KEYS */;
INSERT INTO `cliente` VALUES (1,'Carlos','Ramírez','Sánchez',5511223344,'carlos.ramirez@example.com','RASA910304A56','Calle Falsa 789','Colonia Falsa',12345,'2023-01-01','Activo'),(2,'Ana','Gómez','Martínez',5555667788,'ana.gomez@example.com','GOMT920405B78','Av. Siempre Viva 321','Colonia Nueva',67890,'2023-02-01','Activo'),(9,'Carlos','Ramírez','Sánchez',5511223344,'carlos.ramirez@example.com','RASA910304A5','Calle Falsa 789','Colonia Falsa',12345,'2023-01-01','Activo'),(10,'Ana','Gómez','Martínez',5555667788,'ana.gomez@example.com','GOMT920405B8','Av. Siempre Viva 321','Colonia Nueva',67890,'2023-02-01','Activo'),(11,'Luis','Hernández','López',5599887766,'luis.hernandez@example.com','HELU930506A0','Calle Real 456','Colonia Centro',54321,'2023-03-01','Activo'),(12,'Laura','Pérez','García',5544332211,'laura.perez@example.com','PEGAL940607B2','Av. Principal 654','Colonia Falsa',98765,'2023-04-01','Activo'),(13,'Miguel','Torres','Ramírez',5533221100,'miguel.torres@example.com','MTRR950708A3','Calle Falsa 123','Colonia Centro',12345,'2023-05-01','Activo'),(14,'Sofía','López','Gómez',5522113344,'sofia.lopez@example.com','SLGOM960809A4','Av. Siempre Viva 456','Colonia Nueva',67890,'2023-06-01','Activo');
/*!40000 ALTER TABLE `cliente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detalle_venta`
--

DROP TABLE IF EXISTS `detalle_venta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalle_venta` (
  `ID_DetalleVenta` int NOT NULL AUTO_INCREMENT,
  `Cantidad` int NOT NULL,
  `PrecioUnitario` decimal(10,2) NOT NULL,
  `Subtotal` decimal(10,2) NOT NULL,
  `FK_ID_Venta` int NOT NULL,
  `FK_ID_CatProducto` int NOT NULL,
  PRIMARY KEY (`ID_DetalleVenta`),
  KEY `FK_ID_Venta` (`FK_ID_Venta`),
  KEY `FK_ID_CatProducto` (`FK_ID_CatProducto`),
  CONSTRAINT `detalle_venta_ibfk_1` FOREIGN KEY (`FK_ID_Venta`) REFERENCES `venta` (`ID_Venta`) ON DELETE CASCADE,
  CONSTRAINT `detalle_venta_ibfk_2` FOREIGN KEY (`FK_ID_CatProducto`) REFERENCES `catproducto` (`ID_CatProducto`),
  CONSTRAINT `detalle_venta_chk_1` CHECK ((`Cantidad` > 0)),
  CONSTRAINT `detalle_venta_chk_2` CHECK ((`PrecioUnitario` > 0)),
  CONSTRAINT `detalle_venta_chk_3` CHECK ((`Subtotal` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalle_venta`
--

LOCK TABLES `detalle_venta` WRITE;
/*!40000 ALTER TABLE `detalle_venta` DISABLE KEYS */;
INSERT INTO `detalle_venta` VALUES (13,2,15.00,30.00,7,7),(14,1,150.00,150.00,8,8),(15,3,20.00,60.00,9,9),(16,4,30.00,120.00,10,10),(17,2,25.00,50.00,11,11),(18,1,200.00,200.00,12,12);
/*!40000 ALTER TABLE `detalle_venta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `devolucion`
--

DROP TABLE IF EXISTS `devolucion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `devolucion` (
  `ID_Devolucion` int NOT NULL AUTO_INCREMENT,
  `Descripcion` text NOT NULL,
  `Fecha` date NOT NULL DEFAULT (curdate()),
  `Estado` varchar(20) NOT NULL DEFAULT 'Pendiente',
  `FK_ID_Pedido` int DEFAULT NULL,
  `FK_ID_Venta` int DEFAULT NULL,
  `FK_ID_Usuario` int NOT NULL,
  PRIMARY KEY (`ID_Devolucion`),
  KEY `FK_ID_Pedido` (`FK_ID_Pedido`),
  KEY `FK_ID_Venta` (`FK_ID_Venta`),
  KEY `FK_ID_Usuario` (`FK_ID_Usuario`),
  CONSTRAINT `devolucion_ibfk_1` FOREIGN KEY (`FK_ID_Pedido`) REFERENCES `pedido` (`ID_Pedido`),
  CONSTRAINT `devolucion_ibfk_2` FOREIGN KEY (`FK_ID_Venta`) REFERENCES `venta` (`ID_Venta`),
  CONSTRAINT `devolucion_ibfk_3` FOREIGN KEY (`FK_ID_Usuario`) REFERENCES `empleado` (`Id_Empleado`),
  CONSTRAINT `devolucion_chk_1` CHECK ((`Estado` in (_utf8mb4'Pendiente',_utf8mb4'Aprobada',_utf8mb4'Rechazada',_utf8mb4'Procesada'))),
  CONSTRAINT `devolucion_chk_2` CHECK (((`FK_ID_Pedido` is not null) or (`FK_ID_Venta` is not null)))
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `devolucion`
--

LOCK TABLES `devolucion` WRITE;
/*!40000 ALTER TABLE `devolucion` DISABLE KEYS */;
/*!40000 ALTER TABLE `devolucion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `empleado`
--

DROP TABLE IF EXISTS `empleado`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `empleado` (
  `Id_Empleado` int NOT NULL AUTO_INCREMENT,
  `Nombre_emple` varchar(50) NOT NULL,
  `Ap_Paterno_emple` varchar(50) NOT NULL,
  `Ap_Materno_emple` varchar(50) NOT NULL,
  `CURP_emple` varchar(18) NOT NULL,
  `Sexo` char(1) NOT NULL,
  `RFC_emple` varchar(13) NOT NULL,
  `NSS` bigint NOT NULL,
  `Correo_Electronico` varchar(100) NOT NULL,
  `Telefono_emple` bigint NOT NULL,
  `Padecimientos` text,
  `Calle` varchar(100) NOT NULL,
  `Colonia` varchar(100) NOT NULL,
  `Cod_Postal` int NOT NULL,
  `stoPuesto` varchar(50) NOT NULL,
  `Fecha_Contratacion` date NOT NULL DEFAULT (curdate()),
  `Estado_emple` varchar(20) NOT NULL DEFAULT 'Activo',
  `Contrasena_emple` varchar(255) NOT NULL DEFAULT '12345',
  PRIMARY KEY (`Id_Empleado`),
  UNIQUE KEY `CURP_emple` (`CURP_emple`),
  UNIQUE KEY `RFC_emple` (`RFC_emple`),
  UNIQUE KEY `Correo_Electronico` (`Correo_Electronico`),
  CONSTRAINT `empleado_chk_1` CHECK ((`Sexo` in (_utf8mb4'M',_utf8mb4'F',_utf8mb4'O'))),
  CONSTRAINT `empleado_chk_2` CHECK ((`Estado_emple` in (_utf8mb4'Activo',_utf8mb4'Inactivo',_utf8mb4'Vacaciones',_utf8mb4'Baja')))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `empleado`
--

LOCK TABLES `empleado` WRITE;
/*!40000 ALTER TABLE `empleado` DISABLE KEYS */;
INSERT INTO `empleado` VALUES (1,'Bernardo Adonai','Vasquez','Hernandez','VEHB010101HOCRSR09','M','VAHB010101XXX',9513060854,'ado@gmail.com',5551234567,NULL,'Calle Ejemplo 123','Centro',68000,'GERENTE','2025-04-20','Activo','12345');
/*!40000 ALTER TABLE `empleado` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `factura`
--

DROP TABLE IF EXISTS `factura`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `factura` (
  `ID_Factura` int NOT NULL AUTO_INCREMENT,
  `Fecha` date NOT NULL DEFAULT (curdate()),
  `Total` decimal(12,2) NOT NULL,
  `RFC` varchar(13) DEFAULT NULL,
  `Metodo_Pago` varchar(50) NOT NULL,
  `FK_ID_Venta` int NOT NULL,
  PRIMARY KEY (`ID_Factura`),
  KEY `FK_ID_Venta` (`FK_ID_Venta`),
  CONSTRAINT `factura_ibfk_1` FOREIGN KEY (`FK_ID_Venta`) REFERENCES `venta` (`ID_Venta`),
  CONSTRAINT `factura_chk_1` CHECK ((`Total` >= 0)),
  CONSTRAINT `factura_chk_2` CHECK ((`Metodo_Pago` in (_utf8mb4'Efectivo',_utf8mb4'Tarjeta',_utf8mb4'Transferencia')))
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `factura`
--

LOCK TABLES `factura` WRITE;
/*!40000 ALTER TABLE `factura` DISABLE KEYS */;
INSERT INTO `factura` VALUES (7,'2023-01-01',200.00,'RASA910304A5','Efectivo',7),(8,'2023-01-02',300.00,'GOMT920405B8','Tarjeta',8),(9,'2023-01-03',150.00,'HELU930506A0','Transferencia',9),(10,'2023-01-04',400.00,'PEGAL940607B2','Efectivo',10),(11,'2023-01-05',250.00,'MTRR950708A2','Tarjeta',11),(12,'2023-01-06',350.00,'SLGOM960809A4','Transferencia',12);
/*!40000 ALTER TABLE `factura` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `insumo`
--

DROP TABLE IF EXISTS `insumo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `insumo` (
  `ID_Insumo` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(100) NOT NULL,
  `Stock_Minimo` int NOT NULL,
  `Descripcion` text,
  `Precio` decimal(10,2) NOT NULL,
  `Cantidad` int NOT NULL,
  `IVA` decimal(4,2) NOT NULL DEFAULT '0.16',
  `Estado` varchar(20) NOT NULL DEFAULT 'Disponible',
  `FK_ID_TipoInsumo` int NOT NULL,
  PRIMARY KEY (`ID_Insumo`),
  UNIQUE KEY `Nombre` (`Nombre`),
  KEY `FK_ID_TipoInsumo` (`FK_ID_TipoInsumo`),
  CONSTRAINT `insumo_ibfk_1` FOREIGN KEY (`FK_ID_TipoInsumo`) REFERENCES `tipoinsumo` (`ID_TipoInsumo`),
  CONSTRAINT `insumo_chk_1` CHECK ((`Stock_Minimo` >= 0)),
  CONSTRAINT `insumo_chk_2` CHECK ((`Precio` > 0)),
  CONSTRAINT `insumo_chk_3` CHECK ((`Cantidad` > 0)),
  CONSTRAINT `insumo_chk_4` CHECK ((`IVA` >= 0)),
  CONSTRAINT `insumo_chk_5` CHECK ((`Estado` in (_utf8mb4'Disponible',_utf8mb4'Agotado',_utf8mb4'Descontinuado')))
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `insumo`
--

LOCK TABLES `insumo` WRITE;
/*!40000 ALTER TABLE `insumo` DISABLE KEYS */;
INSERT INTO `insumo` VALUES (1,'Harina de Trigo',50,'Harina de trigo para panadería',20.00,100,0.16,'Disponible',1),(2,'Azúcar Blanca',30,'Azúcar blanca para repostería',15.00,50,0.16,'Disponible',2),(3,'Limones',100,'Limones frescos',5.00,200,0.16,'Disponible',3),(5,'Leche Entera',100,'Leche entera',12.00,200,0.16,'Disponible',5);
/*!40000 ALTER TABLE `insumo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `log`
--

DROP TABLE IF EXISTS `log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `log` (
  `ID_Log` int NOT NULL AUTO_INCREMENT,
  `Fecha` date NOT NULL DEFAULT (curdate()),
  `Hora` time NOT NULL DEFAULT (curtime()),
  `Descripcion` text NOT NULL,
  `Tipo` varchar(50) NOT NULL,
  `FK_ID_Usuario` int NOT NULL,
  PRIMARY KEY (`ID_Log`),
  KEY `FK_ID_Usuario` (`FK_ID_Usuario`),
  CONSTRAINT `log_ibfk_1` FOREIGN KEY (`FK_ID_Usuario`) REFERENCES `empleado` (`Id_Empleado`),
  CONSTRAINT `log_chk_1` CHECK ((`Tipo` in (_utf8mb4'Error',_utf8mb4'Advertencia',_utf8mb4'Información',_utf8mb4'Seguridad')))
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `log`
--

LOCK TABLES `log` WRITE;
/*!40000 ALTER TABLE `log` DISABLE KEYS */;
INSERT INTO `log` VALUES (1,'2025-04-20','20:00:38','Inicio de sesión exitoso para ado@gmail','Seguridad',1),(2,'2025-04-20','20:00:39','Inicio de sesión exitoso para ado@gmail','Seguridad',1),(3,'2025-04-20','20:21:37','Inicio de sesión exitoso para ado@gmail','Seguridad',1),(4,'2025-04-20','20:21:38','Inicio de sesión exitoso para ado@gmail','Seguridad',1),(5,'2025-04-23','15:23:02','Inicio de sesión exitoso para ado@gmail','Seguridad',1),(6,'2025-04-23','15:31:52','Inicio de sesión exitoso para ado@gmail','Seguridad',1),(7,'2025-04-23','15:34:46','Inicio de sesión exitoso para ado@gmail','Seguridad',1),(8,'2025-04-23','19:48:50','Inicio de sesión exitoso para ado@gmail','Seguridad',1),(9,'2025-04-23','19:50:23','Inicio de sesión exitoso para ado@gmail','Seguridad',1),(10,'2025-04-23','19:52:17','Inicio de sesión exitoso para ado@gmail','Seguridad',1),(11,'2025-04-23','19:55:51','Inicio de sesión exitoso para ado@gmail','Seguridad',1),(12,'2025-04-23','19:57:05','Inicio de sesión exitoso para ado@gmail','Seguridad',1),(13,'2025-04-23','19:59:49','Inicio de sesión exitoso para ado@gmail.com','Seguridad',1),(14,'2025-05-07','19:39:46','Inicio de sesión exitoso para ado@gmail.com','Seguridad',1),(15,'2025-05-07','19:40:31','Inicio de sesión exitoso para ado@gmail.com','Seguridad',1),(16,'2025-05-07','19:41:27','Inicio de sesión exitoso para ado@gmail.com','Seguridad',1),(17,'2025-05-07','19:42:56','Inicio de sesión exitoso para ado@gmail.com','Seguridad',1),(18,'2025-05-07','19:44:14','Inicio de sesión exitoso para ado@gmail.com','Seguridad',1),(19,'2025-05-07','19:45:53','Inicio de sesión exitoso para ado@gmail.com','Seguridad',1),(20,'2025-05-07','19:47:36','Inicio de sesión exitoso para ado@gmail.com','Seguridad',1),(21,'2025-05-07','19:48:01','Inicio de sesión exitoso para ado@gmail.com','Seguridad',1),(22,'2025-05-10','22:24:48','Inicio de sesión exitoso para ado@gmail.com','Seguridad',1),(23,'2025-05-10','22:29:21','Inicio de sesión exitoso para ado@gmail.com','Seguridad',1),(24,'2025-05-15','21:45:42','Inicio de sesión exitoso para ado@gmail.com','Seguridad',1),(25,'2025-05-15','21:48:21','Inicio de sesión exitoso para ado@gmail.com','Seguridad',1),(26,'2025-05-15','21:50:42','Inicio de sesión exitoso para ado@gmail.com','Seguridad',1),(27,'2025-05-15','21:51:49','Inicio de sesión exitoso para ado@gmail.com','Seguridad',1),(28,'2025-05-15','22:56:57','Inicio de sesión exitoso para ado@gmail.com','Seguridad',1),(29,'2025-05-15','23:20:53','Inicio de sesión exitoso para ado@gmail.com','Seguridad',1),(30,'2025-05-15','23:40:33','Inicio de sesión exitoso para ado@gmail.com','Seguridad',1),(31,'2025-05-15','23:41:19','Inicio de sesión exitoso para ado@gmail.com','Seguridad',1);
/*!40000 ALTER TABLE `log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `materiaprima`
--

DROP TABLE IF EXISTS `materiaprima`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `materiaprima` (
  `ID_MateriaPrima` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(100) NOT NULL,
  `Cantidad` int NOT NULL,
  `Descripcion` text,
  `Precio` decimal(10,2) NOT NULL,
  `IVA` decimal(4,2) NOT NULL DEFAULT '0.16',
  `Stock` int NOT NULL DEFAULT '0',
  `Estado` varchar(20) NOT NULL DEFAULT 'Disponible',
  `FK_ID_MedidaCantidad` int NOT NULL,
  `FK_ID_TipoMateriaPrima` int NOT NULL,
  PRIMARY KEY (`ID_MateriaPrima`),
  UNIQUE KEY `Nombre` (`Nombre`),
  KEY `FK_ID_MedidaCantidad` (`FK_ID_MedidaCantidad`),
  KEY `FK_ID_TipoMateriaPrima` (`FK_ID_TipoMateriaPrima`),
  CONSTRAINT `materiaprima_ibfk_1` FOREIGN KEY (`FK_ID_MedidaCantidad`) REFERENCES `medidacantidad` (`ID_MedidaCantidad`),
  CONSTRAINT `materiaprima_ibfk_2` FOREIGN KEY (`FK_ID_TipoMateriaPrima`) REFERENCES `tipomateriaprima` (`ID_TipoMateriaPrima`),
  CONSTRAINT `materiaprima_chk_1` CHECK ((`Cantidad` > 0)),
  CONSTRAINT `materiaprima_chk_2` CHECK ((`Precio` > 0)),
  CONSTRAINT `materiaprima_chk_3` CHECK ((`IVA` >= 0)),
  CONSTRAINT `materiaprima_chk_4` CHECK ((`Stock` >= 0)),
  CONSTRAINT `materiaprima_chk_5` CHECK ((`Estado` in (_utf8mb4'Disponible',_utf8mb4'Agotado',_utf8mb4'Descontinuado')))
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `materiaprima`
--

LOCK TABLES `materiaprima` WRITE;
/*!40000 ALTER TABLE `materiaprima` DISABLE KEYS */;
INSERT INTO `materiaprima` VALUES (1,'Leche',100,'Leche entera',10.00,0.16,50,'Disponible',1,1),(2,'Manzana',200,'Manzana roja',5.00,0.16,100,'Disponible',2,2),(3,'Zanahoria',300,'Zanahoria fresca',3.00,0.16,150,'Disponible',3,3),(5,'Arroz',500,'Arroz blanco',20.00,0.16,250,'Disponible',1,5),(6,'Sal',1000,'Sal de mesa',5.00,0.16,500,'Disponible',4,6);
/*!40000 ALTER TABLE `materiaprima` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medidacantidad`
--

DROP TABLE IF EXISTS `medidacantidad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medidacantidad` (
  `ID_MedidaCantidad` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(50) NOT NULL,
  `Abreviatura` varchar(10) NOT NULL,
  PRIMARY KEY (`ID_MedidaCantidad`),
  UNIQUE KEY `Nombre` (`Nombre`),
  UNIQUE KEY `Abreviatura` (`Abreviatura`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medidacantidad`
--

LOCK TABLES `medidacantidad` WRITE;
/*!40000 ALTER TABLE `medidacantidad` DISABLE KEYS */;
INSERT INTO `medidacantidad` VALUES (1,'Kilogramo','kg'),(2,'Litro','L'),(3,'Pieza','pz'),(4,'Gramo','g'),(5,'Mililitro','mL'),(6,'Caja','cj');
/*!40000 ALTER TABLE `medidacantidad` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pedido`
--

DROP TABLE IF EXISTS `pedido`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pedido` (
  `ID_Pedido` int NOT NULL AUTO_INCREMENT,
  `Plazo` int NOT NULL,
  `Fecha` date NOT NULL DEFAULT (curdate()),
  `Exigencia` text,
  `Estado` varchar(20) NOT NULL DEFAULT 'Pendiente',
  `Total` decimal(12,2) NOT NULL DEFAULT '0.00',
  `FK_ID_Proveedor` int NOT NULL,
  PRIMARY KEY (`ID_Pedido`),
  KEY `FK_ID_Proveedor` (`FK_ID_Proveedor`),
  CONSTRAINT `pedido_ibfk_1` FOREIGN KEY (`FK_ID_Proveedor`) REFERENCES `proveedor` (`Id_Proveedor`),
  CONSTRAINT `pedido_chk_1` CHECK ((`Plazo` > 0)),
  CONSTRAINT `pedido_chk_2` CHECK ((`Estado` in (_utf8mb4'Pendiente',_utf8mb4'En proceso',_utf8mb4'Completado',_utf8mb4'Cancelado'))),
  CONSTRAINT `pedido_chk_3` CHECK ((`Total` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedido`
--

LOCK TABLES `pedido` WRITE;
/*!40000 ALTER TABLE `pedido` DISABLE KEYS */;
INSERT INTO `pedido` VALUES (7,7,'2023-01-01','Entrega en 7 días','Pendiente',1000.00,1),(8,14,'2023-01-02','Entrega en 14 días','Pendiente',2000.00,2),(9,5,'2023-01-03','Entrega en 5 días','En proceso',1500.00,17),(10,10,'2023-01-04','Entrega en 10 días','Completado',1200.00,18),(11,8,'2023-01-05','Entrega en 8 días','Pendiente',1800.00,19),(12,6,'2023-01-06','Entrega en 6 días','En proceso',1300.00,20);
/*!40000 ALTER TABLE `pedido` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pedido_insumo`
--

DROP TABLE IF EXISTS `pedido_insumo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pedido_insumo` (
  `ID_Pedido_Insumo` int NOT NULL AUTO_INCREMENT,
  `Precio` decimal(10,2) NOT NULL,
  `Unidades` int NOT NULL,
  `Cancelado` tinyint(1) NOT NULL DEFAULT '0',
  `FK_ID_Pedido` int NOT NULL,
  `FK_ID_Insumo` int NOT NULL,
  PRIMARY KEY (`ID_Pedido_Insumo`),
  KEY `FK_ID_Pedido` (`FK_ID_Pedido`),
  KEY `FK_ID_Insumo` (`FK_ID_Insumo`),
  CONSTRAINT `pedido_insumo_ibfk_1` FOREIGN KEY (`FK_ID_Pedido`) REFERENCES `pedido` (`ID_Pedido`) ON DELETE CASCADE,
  CONSTRAINT `pedido_insumo_ibfk_2` FOREIGN KEY (`FK_ID_Insumo`) REFERENCES `insumo` (`ID_Insumo`),
  CONSTRAINT `pedido_insumo_chk_1` CHECK ((`Precio` > 0)),
  CONSTRAINT `pedido_insumo_chk_2` CHECK ((`Unidades` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedido_insumo`
--

LOCK TABLES `pedido_insumo` WRITE;
/*!40000 ALTER TABLE `pedido_insumo` DISABLE KEYS */;
INSERT INTO `pedido_insumo` VALUES (13,20.00,50,0,8,1),(14,15.00,30,0,9,2),(15,5.00,100,0,10,3),(16,10.00,150,0,11,4),(17,12.00,200,0,12,5),(18,50.00,50,0,7,6);
/*!40000 ALTER TABLE `pedido_insumo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pedido_materiaprima`
--

DROP TABLE IF EXISTS `pedido_materiaprima`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pedido_materiaprima` (
  `FK_ID_Pedido` int NOT NULL,
  `FK_ID_MateriaPrima` int NOT NULL,
  `Precio` decimal(10,2) NOT NULL,
  `Unidades` int NOT NULL,
  `Cancelado` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`FK_ID_Pedido`,`FK_ID_MateriaPrima`),
  KEY `FK_ID_MateriaPrima` (`FK_ID_MateriaPrima`),
  CONSTRAINT `pedido_materiaprima_ibfk_1` FOREIGN KEY (`FK_ID_Pedido`) REFERENCES `pedido` (`ID_Pedido`) ON DELETE CASCADE,
  CONSTRAINT `pedido_materiaprima_ibfk_2` FOREIGN KEY (`FK_ID_MateriaPrima`) REFERENCES `materiaprima` (`ID_MateriaPrima`),
  CONSTRAINT `pedido_materiaprima_chk_1` CHECK ((`Precio` > 0)),
  CONSTRAINT `pedido_materiaprima_chk_2` CHECK ((`Unidades` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedido_materiaprima`
--

LOCK TABLES `pedido_materiaprima` WRITE;
/*!40000 ALTER TABLE `pedido_materiaprima` DISABLE KEYS */;
INSERT INTO `pedido_materiaprima` VALUES (7,1,10.00,100,0),(8,2,5.00,200,0),(9,3,3.00,300,0),(10,4,50.00,50,0),(11,5,20.00,500,0),(12,6,5.00,1000,0);
/*!40000 ALTER TABLE `pedido_materiaprima` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `produccion`
--

DROP TABLE IF EXISTS `produccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `produccion` (
  `ID_Produccion` int NOT NULL AUTO_INCREMENT,
  `Unidades` int NOT NULL,
  `CantidadInicial` int NOT NULL,
  `Fecha` date NOT NULL DEFAULT (curdate()),
  `FK_ID_CatProducto` int NOT NULL,
  `FK_ID_Empleado` int NOT NULL,
  PRIMARY KEY (`ID_Produccion`),
  KEY `FK_ID_CatProducto` (`FK_ID_CatProducto`),
  KEY `FK_ID_Empleado` (`FK_ID_Empleado`),
  CONSTRAINT `produccion_ibfk_1` FOREIGN KEY (`FK_ID_CatProducto`) REFERENCES `catproducto` (`ID_CatProducto`),
  CONSTRAINT `produccion_ibfk_2` FOREIGN KEY (`FK_ID_Empleado`) REFERENCES `empleado` (`Id_Empleado`),
  CONSTRAINT `produccion_chk_1` CHECK ((`Unidades` > 0)),
  CONSTRAINT `produccion_chk_2` CHECK ((`CantidadInicial` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `produccion`
--

LOCK TABLES `produccion` WRITE;
/*!40000 ALTER TABLE `produccion` DISABLE KEYS */;
INSERT INTO `produccion` VALUES (21,10,100,'2023-01-01',25,1),(22,5,50,'2023-01-02',25,1),(23,20,200,'2023-01-03',25,1),(24,15,150,'2023-01-04',25,1),(25,10,100,'2023-01-05',25,1),(26,5,50,'2023-01-06',25,1);
/*!40000 ALTER TABLE `produccion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proveedor`
--

DROP TABLE IF EXISTS `proveedor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proveedor` (
  `Id_Proveedor` int NOT NULL AUTO_INCREMENT,
  `Nombre_prov_proveedor` varchar(50) NOT NULL,
  `Ap_paterno_prov` varchar(50) DEFAULT NULL,
  `Ap_materno_prov` varchar(50) DEFAULT NULL,
  `Razon_Social` varchar(100) NOT NULL,
  `RFC` varchar(13) NOT NULL,
  `Correo_prov` varchar(100) NOT NULL,
  `Telefono_prov` bigint NOT NULL,
  `Direccion` text NOT NULL,
  `Estado` varchar(20) NOT NULL DEFAULT 'Activo',
  PRIMARY KEY (`Id_Proveedor`),
  UNIQUE KEY `RFC` (`RFC`),
  CONSTRAINT `proveedor_chk_1` CHECK ((`Estado` in (_utf8mb4'Activo',_utf8mb4'Inactivo',_utf8mb4'Suspendido')))
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proveedor`
--

LOCK TABLES `proveedor` WRITE;
/*!40000 ALTER TABLE `proveedor` DISABLE KEYS */;
INSERT INTO `proveedor` VALUES (1,'Juan','Pérez','García','Harinas Pérez S.A. de C.V.','HAPG890101A12','juan.perez@harinas.com',5512345678,'Calle Falsa 123, Colonia Centro, CDMX','Activo'),(2,'María','López','Hernández','Insumos López S.A. de C.V.','ILHM900202B34','maria.lopez@insumos.com',5587654321,'Av. Siempre Viva 456, Colonia Nueva, CDMX','Activo'),(17,'Luis','Martínez','Ramírez','Productos Martínez S.A. de C.V.','PMRM910304A56','luis.martinez@productos.com',5511223344,'Calle Real 789, Colonia Falsa, CDMX','Activo'),(18,'Ana','Gómez','Sánchez','Distribuidora Gómez S.A. de C.V.','DGSA920405B8','ana.gomez@distribuidora.com',5555667788,'Av. Principal 321, Colonia Nueva, CDMX','Activo'),(19,'Carlos','Ramírez','López','Alimentos Ramírez S.A. de C.V.','ARLR930506A0','carlos.ramirez@alimentos.com',5599887766,'Calle Falsa 456, Colonia Centro, CDMX','Activo'),(20,'Laura','Pérez','García','Bebidas Pérez S.A. de C.V.','BPGAL940607B2','laura.perez@bebidas.com',5544332211,'Av. Siempre Viva 654, Colonia Falsa, CDMX','Activo');
/*!40000 ALTER TABLE `proveedor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proveedor_insumo`
--

DROP TABLE IF EXISTS `proveedor_insumo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proveedor_insumo` (
  `FK_ID_Proveedor` int NOT NULL,
  `FK_ID_Insumo` int NOT NULL,
  `Estado` varchar(20) NOT NULL DEFAULT 'Activo',
  `Precio_Referencia` decimal(10,2) NOT NULL,
  `Tiempo_Entrega` int NOT NULL,
  PRIMARY KEY (`FK_ID_Proveedor`,`FK_ID_Insumo`),
  KEY `FK_ID_Insumo` (`FK_ID_Insumo`),
  CONSTRAINT `proveedor_insumo_ibfk_1` FOREIGN KEY (`FK_ID_Proveedor`) REFERENCES `proveedor` (`Id_Proveedor`) ON DELETE CASCADE,
  CONSTRAINT `proveedor_insumo_ibfk_2` FOREIGN KEY (`FK_ID_Insumo`) REFERENCES `insumo` (`ID_Insumo`) ON DELETE CASCADE,
  CONSTRAINT `proveedor_insumo_chk_1` CHECK ((`Estado` in (_utf8mb4'Activo',_utf8mb4'Inactivo'))),
  CONSTRAINT `proveedor_insumo_chk_2` CHECK ((`Precio_Referencia` > 0)),
  CONSTRAINT `proveedor_insumo_chk_3` CHECK ((`Tiempo_Entrega` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proveedor_insumo`
--

LOCK TABLES `proveedor_insumo` WRITE;
/*!40000 ALTER TABLE `proveedor_insumo` DISABLE KEYS */;
/*!40000 ALTER TABLE `proveedor_insumo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proveedor_materiaprima`
--

DROP TABLE IF EXISTS `proveedor_materiaprima`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proveedor_materiaprima` (
  `FK_ID_MateriaPrima` int NOT NULL,
  `FK_ID_Proveedor` int NOT NULL,
  `Estado` varchar(20) NOT NULL DEFAULT 'Activo',
  `Precio_Referencia` decimal(10,2) NOT NULL,
  `Tiempo_Entrega` int NOT NULL,
  PRIMARY KEY (`FK_ID_MateriaPrima`,`FK_ID_Proveedor`),
  KEY `FK_ID_Proveedor` (`FK_ID_Proveedor`),
  CONSTRAINT `proveedor_materiaprima_ibfk_1` FOREIGN KEY (`FK_ID_MateriaPrima`) REFERENCES `materiaprima` (`ID_MateriaPrima`) ON DELETE CASCADE,
  CONSTRAINT `proveedor_materiaprima_ibfk_2` FOREIGN KEY (`FK_ID_Proveedor`) REFERENCES `proveedor` (`Id_Proveedor`) ON DELETE CASCADE,
  CONSTRAINT `proveedor_materiaprima_chk_1` CHECK ((`Estado` in (_utf8mb4'Activo',_utf8mb4'Inactivo'))),
  CONSTRAINT `proveedor_materiaprima_chk_2` CHECK ((`Precio_Referencia` > 0)),
  CONSTRAINT `proveedor_materiaprima_chk_3` CHECK ((`Tiempo_Entrega` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proveedor_materiaprima`
--

LOCK TABLES `proveedor_materiaprima` WRITE;
/*!40000 ALTER TABLE `proveedor_materiaprima` DISABLE KEYS */;
/*!40000 ALTER TABLE `proveedor_materiaprima` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `receta`
--

DROP TABLE IF EXISTS `receta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `receta` (
  `ID_Receta` int NOT NULL AUTO_INCREMENT,
  `Nombre_receta` varchar(100) NOT NULL,
  `Descripcion` text,
  `Tiempo_Preparacion` int NOT NULL,
  `Instrucciones` text NOT NULL,
  PRIMARY KEY (`ID_Receta`),
  UNIQUE KEY `Nombre_receta` (`Nombre_receta`),
  CONSTRAINT `receta_chk_1` CHECK ((`Tiempo_Preparacion` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `receta`
--

LOCK TABLES `receta` WRITE;
/*!40000 ALTER TABLE `receta` DISABLE KEYS */;
INSERT INTO `receta` VALUES (1,'Receta Pan Dulce','Pan suave con cobertura dulce',60,'Mezclar ingredientes, amasar, hornear 30 min.'),(2,'Receta Pastel Cumpleaños','Pastel de vainilla con betún',90,'Preparar mezcla, hornear, decorar.'),(3,'Receta Galleta Choco','Galletas con chispas de chocolate',45,'Mezclar, formar bolitas, hornear.'),(4,'Receta Pan Salado','Pan estilo baguette',70,'Fermentar masa, formar baguettes, hornear.'),(5,'Receta Pastel Boda','Pastel de tres pisos',120,'Preparar por capas, armar y decorar.'),(6,'Receta Galleta Avena','Galletas con avena y pasas',50,'Mezclar ingredientes y hornear.'),(13,'Pan Francés','Receta tradicional de pan francés',120,'Mezclar ingredientes, amasar, dejar reposar y hornear.'),(14,'Pastel de Chocolate','Receta de pastel de chocolate',180,'Mezclar ingredientes, hornear y decorar.');
/*!40000 ALTER TABLE `receta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subtipoproducto`
--

DROP TABLE IF EXISTS `subtipoproducto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subtipoproducto` (
  `ID_SubtipoProducto` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(50) NOT NULL,
  `FK_ID_TipoProducto` int NOT NULL,
  PRIMARY KEY (`ID_SubtipoProducto`),
  UNIQUE KEY `Nombre` (`Nombre`,`FK_ID_TipoProducto`),
  KEY `FK_ID_TipoProducto` (`FK_ID_TipoProducto`),
  CONSTRAINT `subtipoproducto_ibfk_1` FOREIGN KEY (`FK_ID_TipoProducto`) REFERENCES `tipoproducto` (`Id_TipoProducto`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subtipoproducto`
--

LOCK TABLES `subtipoproducto` WRITE;
/*!40000 ALTER TABLE `subtipoproducto` DISABLE KEYS */;
INSERT INTO `subtipoproducto` VALUES (6,'Galleta de avena',3),(5,'Galleta de chocolate',3),(7,'Pan',1),(1,'Pan dulce',1),(2,'Pan salado',1),(8,'Pastel',2),(4,'Pastel de boda',2),(3,'Pastel de cumpleaños',2);
/*!40000 ALTER TABLE `subtipoproducto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipoinsumo`
--

DROP TABLE IF EXISTS `tipoinsumo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tipoinsumo` (
  `ID_TipoInsumo` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(50) NOT NULL,
  `Descripcion` text,
  PRIMARY KEY (`ID_TipoInsumo`),
  UNIQUE KEY `Nombre` (`Nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipoinsumo`
--

LOCK TABLES `tipoinsumo` WRITE;
/*!40000 ALTER TABLE `tipoinsumo` DISABLE KEYS */;
INSERT INTO `tipoinsumo` VALUES (1,'Harina','Insumo básico para panadería'),(2,'Azúcar','Insumo básico para repostería'),(3,'Limones','Fruta cítrica'),(4,'Papas','Tubérculo para snacks'),(5,'Leche','Producto lácteo'),(6,'Pollo','Carne de pollo');
/*!40000 ALTER TABLE `tipoinsumo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipomateriaprima`
--

DROP TABLE IF EXISTS `tipomateriaprima`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tipomateriaprima` (
  `ID_TipoMateriaPrima` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(50) NOT NULL,
  `Descripcion` text,
  PRIMARY KEY (`ID_TipoMateriaPrima`),
  UNIQUE KEY `Nombre` (`Nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipomateriaprima`
--

LOCK TABLES `tipomateriaprima` WRITE;
/*!40000 ALTER TABLE `tipomateriaprima` DISABLE KEYS */;
INSERT INTO `tipomateriaprima` VALUES (1,'Lácteos','Productos lácteos'),(2,'Frutas','Frutas frescas'),(3,'Verduras','Verduras frescas'),(4,'Carnes','Carnes variadas'),(5,'Granos','Granos y semillas'),(6,'Especias','Especias y condimentos');
/*!40000 ALTER TABLE `tipomateriaprima` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipoproducto`
--

DROP TABLE IF EXISTS `tipoproducto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tipoproducto` (
  `Id_TipoProducto` int NOT NULL AUTO_INCREMENT,
  `Nombre_prod` varchar(50) NOT NULL,
  `Descripcion` text,
  PRIMARY KEY (`Id_TipoProducto`),
  UNIQUE KEY `Nombre_prod` (`Nombre_prod`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipoproducto`
--

LOCK TABLES `tipoproducto` WRITE;
/*!40000 ALTER TABLE `tipoproducto` DISABLE KEYS */;
INSERT INTO `tipoproducto` VALUES (1,'Pan dulce','Productos de panadería con sabores dulces'),(2,'Pan salado','Productos como baguettes y bolillos'),(3,'Pasteles','Pasteles para ocasiones especiales'),(4,'Galletas','Galletas de distintos sabores'),(5,'Panadería','Productos de panadería'),(6,'Repostería','Productos de repostería');
/*!40000 ALTER TABLE `tipoproducto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `venta`
--

DROP TABLE IF EXISTS `venta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `venta` (
  `ID_Venta` int NOT NULL AUTO_INCREMENT,
  `Fecha_venta` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Total_venta` decimal(12,2) NOT NULL,
  `Estado` varchar(20) NOT NULL DEFAULT 'Completada',
  `FK_ID_Cliente` int DEFAULT NULL,
  `FK_ID_Empleado` int NOT NULL,
  PRIMARY KEY (`ID_Venta`),
  KEY `FK_ID_Cliente` (`FK_ID_Cliente`),
  KEY `FK_ID_Empleado` (`FK_ID_Empleado`),
  CONSTRAINT `venta_ibfk_1` FOREIGN KEY (`FK_ID_Cliente`) REFERENCES `cliente` (`Id_Cliente`),
  CONSTRAINT `venta_ibfk_2` FOREIGN KEY (`FK_ID_Empleado`) REFERENCES `empleado` (`Id_Empleado`),
  CONSTRAINT `venta_chk_1` CHECK ((`Total_venta` >= 0)),
  CONSTRAINT `venta_chk_2` CHECK ((`Estado` in (_utf8mb4'Completada',_utf8mb4'Cancelada',_utf8mb4'Devuelta')))
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `venta`
--

LOCK TABLES `venta` WRITE;
/*!40000 ALTER TABLE `venta` DISABLE KEYS */;
INSERT INTO `venta` VALUES (7,'2023-01-01 16:00:00',200.00,'Completada',1,1),(8,'2023-01-02 17:00:00',300.00,'Completada',2,1),(9,'2023-01-03 18:00:00',150.00,'Cancelada',9,1),(10,'2023-01-04 19:00:00',400.00,'Devuelta',10,1),(11,'2023-01-05 20:00:00',250.00,'Completada',11,1),(12,'2023-01-06 21:00:00',350.00,'Completada',12,1);
/*!40000 ALTER TABLE `venta` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-18 19:40:41
