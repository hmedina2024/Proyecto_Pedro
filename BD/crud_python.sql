CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name_surname` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `email_user` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `pass_user` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `rol` varchar(45) COLLATE utf8mb4_general_ci NOT NULL,
  `created_user` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


CREATE TABLE `tbl_contratos` (
  `id_contrato` int NOT NULL AUTO_INCREMENT,
  `documento` int NOT NULL,
  `razon_social` varchar(100) DEFAULT NULL,
  `cantidad` int DEFAULT NULL,
  `objeto_contractual` mediumtext,
  `fecha_inicio` timestamp NOT NULL,
  `fecha_fin` timestamp NOT NULL,
  `fecha_registro` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `usuario_registro` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id_contrato`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `tbl_innovacion` (
  `id_innovacion` int NOT NULL AUTO_INCREMENT,
  `titulo_idea` varchar(100) NOT NULL,
  `fecha_inicio` date NOT NULL,
  `descripcion_idea` varchar(500) DEFAULT NULL,
  `espacio_problema` varchar(500) DEFAULT NULL,
  `aspecto` varchar(45) DEFAULT NULL,
  `roles` varchar(500) DEFAULT NULL,
  `estrategias` varchar(500) DEFAULT NULL,
  `diseño` varchar(500) DEFAULT NULL,
  `implementacion` varchar(500) DEFAULT NULL,
  `fecha_plazo` date DEFAULT NULL,
  `evaluacion` varchar(500) DEFAULT NULL,
  `aprender_planear` varchar(500) DEFAULT NULL,
  `ajustes` varchar(500) DEFAULT NULL,
  `fecha_fin` date DEFAULT NULL,
  `fecha_registro` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `usuario_registro` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id_innovacion`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `tbl_percepcion` (
  `id_percepcion` int NOT NULL AUTO_INCREMENT,
  `tipo` varchar(100) NOT NULL,
  `pregunta` varchar(200) NOT NULL,
  `respuesta` int DEFAULT NULL,
  `fecha_registro` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `usuario_registro` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id_percepcion`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;