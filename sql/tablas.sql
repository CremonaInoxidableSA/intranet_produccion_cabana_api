CREATE TABLE Pallets (
    id_pallet      INT AUTO_INCREMENT PRIMARY KEY,
    codigo         VARCHAR(50)  NOT NULL UNIQUE,
    tipo           VARCHAR(50)  NOT NULL,
    fecha_compra   DATE         NOT NULL,
    estado         TINYINT(1)   NOT NULL DEFAULT 0, -- 1=activo, 0=inactivo
    actualizado    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_pallet_estado (estado),
    INDEX idx_pallet_tipo (tipo)
);

CREATE TABLE Productos (
    id_producto    INT AUTO_INCREMENT PRIMARY KEY,
    nombre         VARCHAR(150) NOT NULL,
    codigo         VARCHAR(50)  NOT NULL UNIQUE,
    empresa        VARCHAR(100) NOT NULL,
    tipo           VARCHAR(50)  NOT NULL,
    INDEX idx_producto_empresa (empresa),
    INDEX idx_producto_tipo (tipo)
);

CREATE TABLE Pallets_Productos (
    id_pallet_producto  INT AUTO_INCREMENT PRIMARY KEY,
    id_pallet           INT          NOT NULL,
    id_producto         INT          NOT NULL,
    cantidad_producto   INT          NOT NULL DEFAULT 0,
    lote                VARCHAR(50),
    fecha_vencimiento   DATE,
    fecha_ingreso       DATE         NOT NULL,
    CONSTRAINT fk_pp_pallet   FOREIGN KEY (id_pallet)   REFERENCES Pallets(id_pallet)     ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_pp_producto FOREIGN KEY (id_producto) REFERENCES Productos(id_producto) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_pp_producto (id_producto),
    INDEX idx_pp_vencimiento (fecha_vencimiento)
);

CREATE TABLE Cargas_Descargas (
    id_carga_descarga   INT AUTO_INCREMENT PRIMARY KEY,
    tipo                ENUM('carga','descarga') NOT NULL,
    id_pallet           INT          NOT NULL,
    id_producto         INT          NOT NULL,
    cantidad_anterior   INT          NOT NULL,
    cantidad_modificada INT          NOT NULL,
    peso_kg             FLOAT,
    motivo              VARCHAR(255),
    usuario             VARCHAR(100) NOT NULL,
    fecha_carga_descarga DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cd_pallet   FOREIGN KEY (id_pallet)   REFERENCES Pallets(id_pallet)     ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_cd_producto FOREIGN KEY (id_producto) REFERENCES Productos(id_producto) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_cd_fecha (fecha_carga_descarga),
    INDEX idx_cd_tipo (tipo),
    INDEX idx_cd_pallet (id_pallet)
);

CREATE TABLE Movimientos (
    id_movimiento               INT AUTO_INCREMENT PRIMARY KEY,
    tipo                        ENUM('ajuste','traslado') NOT NULL,
    id_pallet_producto_origen   INT,
    id_pallet_producto_destino  INT,
    id_producto                 INT          NOT NULL,
    cantidad_anterior_origen    INT          NOT NULL DEFAULT 0,
    cantidad_anterior_destino   INT          NOT NULL DEFAULT 0,
    cantidad_modificada         INT          NOT NULL,
    motivo                      VARCHAR(255),
    usuario                     VARCHAR(100) NOT NULL,
    fecha_movimiento            DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_mv_origen    FOREIGN KEY (id_pallet_producto_origen)  REFERENCES Pallets_Productos(id_pallet_producto) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_mv_destino   FOREIGN KEY (id_pallet_producto_destino) REFERENCES Pallets_Productos(id_pallet_producto) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_mv_producto  FOREIGN KEY (id_producto)                REFERENCES Productos(id_producto)              ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_mv_fecha (fecha_movimiento),
    INDEX idx_mv_tipo (tipo),
    INDEX idx_mv_producto (id_producto)
);