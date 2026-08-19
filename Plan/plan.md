**UNIVERSIDAD MARIANO GÁLVEZ DE GUATEMALA
FACULTAD DE INGENIERIA EN SISTEMAS DE INFORMACIÓN
LICENCIATURA EN INGENIERÍA EN SISTEMAS DE
INFORMACIÓN CENTRO UNIVERSITARIO DE
CHIMALTENANGO**

DECIMO CICLO
ASEGURAMIENTO DE LA CALIDAD DE SOFTWARE

![](data:image/png;base64...)

Tarea
**PRIMERA FASE**

Wincer Daniel Córdova Marroquín 1990-22-8308
Daniel Angel Ambrocio Coj 1990-22-13443

Wilson Adolfo Coc Avila - 1990-22-1148
----------------------------------------------
ESTUDIANTES

Tabla de contenido

[Definición del proyecto 4](#_Toc237721561)

[Nombre del proyecto 4](#_Toc237721562)

[Descripción del proyecto 4](#_Toc237721563)

[Problemática 4](#_Toc237721564)

[Justificación 5](#_Toc237721565)

[Objetivos 6](#_Toc237721566)

[Objetivo general 6](#_Toc237721567)

[Objetivos específicos 6](#_Toc237721568)

[Alcance del proyecto 6](#_Toc237721569)

[Funcionalidades incluidas 6](#_Toc237721570)

[Gestión de casas 6](#_Toc237721571)

[Gestión de vecinos 7](#_Toc237721572)

[Gestión de familias 7](#_Toc237721573)

[Gestión de parentescos 7](#_Toc237721574)

[Gestión de deudas 7](#_Toc237721575)

[Gestión de multas 8](#_Toc237721576)

[Gestión de usuarios 8](#_Toc237721577)

[Gestión de roles 8](#_Toc237721578)

[Actores del sistema 8](#_Toc237721579)

[Requerimientos funcionales 9](#_Toc237721580)

[Requerimientos no funcionales 10](#_Toc237721581)

[Tecnologías seleccionadas 11](#_Toc237721582)

[¿Por qué utilizar estas herramientas? 12](#_Toc237721583)

[HTML, CSS y Bootstrap 5 12](#_Toc237721584)

[Python 12](#_Toc237721585)

[PostgreSQL 12](#_Toc237721586)

[Scrum 12](#_Toc237721587)

[Arquitectura propuesta 13](#_Toc237721588)

[Diseño preliminar de la base de datos 14](#_Toc237721589)

[Módulos del sistema 16](#_Toc237721590)

[Scrum aplicado al proyecto 17](#_Toc237721591)

[Roles Scrum 17](#_Toc237721592)

[Product Owner 17](#_Toc237721593)

[Scrum Master 17](#_Toc237721594)

[Equipo de desarrollo 17](#_Toc237721595)

[Product Backlog inicial 17](#_Toc237721596)

[Sprints iniciales 18](#_Toc237721597)

[Sprint 1 18](#_Toc237721598)

[Sprint 3 18](#_Toc237721599)

[Sprint 4 18](#_Toc237721600)

[Sprint 5 19](#_Toc237721601)

[Sprint 6 19](#_Toc237721602)

# Definición del proyecto

## Nombre del proyecto

**Sistema Web para la Gestión Administrativa de una Colonia Residencial**

## Descripción del proyecto

El proyecto consiste en desarrollar una aplicación web destinada a la administración y control de una colonia residencial conformada por aproximadamente **500 casas**.

El sistema permitirá administrar la información relacionada con las viviendas, vecinos, familias, hijos y encargados, así como las relaciones de parentesco existentes entre los integrantes de cada familia.

Además, permitirá llevar un control de las deudas y multas asociadas a los residentes, así como la administración de los usuarios que tendrán acceso al sistema y la asignación de diferentes roles y permisos.

El desarrollo del proyecto se realizará aplicando la metodología ágil **Scrum**, utilizando sus diferentes fases y elementos para organizar el análisis, diseño, desarrollo, pruebas y evolución del sistema.

# Problemática

La administración de una colonia residencial requiere manejar una cantidad considerable de información relacionada con las viviendas, vecinos, familias, encargados, parentescos, deudas y multas.

Cuando esta información es administrada mediante registros manuales, hojas de cálculo o diferentes medios separados, puede resultar complicado mantener la información organizada, actualizada y disponible para las personas encargadas de la administración.

Además, la ausencia de un sistema centralizado puede dificultar la consulta de información sobre los residentes, el seguimiento de deudas y multas, y la administración de los usuarios responsables de gestionar el sistema.

Por esta razón, se propone desarrollar una aplicación web que centralice la información administrativa de la colonia y facilite el control de sus diferentes procesos.

# Justificación

**¿Por qué vale la pena hacer el proyecto?**

La implementación del sistema permitirá centralizar la información administrativa de la colonia residencial en una única aplicación web.

El sistema facilitará el registro y consulta de vecinos, familias, hijos y encargados, permitiendo establecer las relaciones de parentesco correspondientes. También permitirá mantener un control de las deudas individuales y multas, así como gestionar los usuarios que tendrán acceso al sistema.

La utilización de roles permitirá organizar el acceso a las diferentes funcionalidades de acuerdo con las responsabilidades de cada usuario.

Desde el punto de vista académico, el proyecto permitirá aplicar la metodología Scrum durante las diferentes etapas del desarrollo de software, permitiendo poner en práctica conceptos de análisis, diseño, desarrollo, pruebas, control de calidad y gestión de proyectos.

# Objetivos

## Objetivo general

Desarrollar una aplicación web para la gestión administrativa de una colonia residencial de aproximadamente 500 casas, utilizando la metodología Scrum para organizar las diferentes etapas del desarrollo del software.

## Objetivos específicos

1. Diseñar una base de datos para almacenar la información de las viviendas, vecinos, familias, hijos, encargados, parentescos, deudas, multas y usuarios del sistema.
2. Desarrollar un módulo para la gestión de las casas y residentes de la colonia.
3. Implementar la gestión de familias y las relaciones de parentesco entre sus integrantes.
4. Implementar un módulo para el control de deudas individuales de los residentes.
5. Implementar un módulo para el registro y control de multas.
6. Desarrollar un sistema de usuarios basado en roles para controlar el acceso a las funcionalidades.
7. Desarrollar una interfaz web utilizando HTML, CSS y Bootstrap 5.
8. Implementar la lógica del sistema mediante Python.
9. Utilizar PostgreSQL como sistema gestor de base de datos.
10. Aplicar Scrum durante la planificación, desarrollo, revisión y mejora continua del proyecto.

# Alcance del proyecto

## Funcionalidades incluidas

El sistema contemplará inicialmente:

## Gestión de casas

* Registro de casas.
* Identificación de cada casa.
* Consulta del estado de una casa.
* Asociación de residentes a una vivienda.

## Gestión de vecinos

* Registro de vecinos.
* Actualización de información.
* Consulta de vecinos.
* Asociación del vecino con una casa.

## Gestión de familias

* Registro de familias.
* Asociación de integrantes.
* Registro de hijos.
* Registro de encargados.

## Gestión de parentescos

Permitirá establecer relaciones como:

* Padre
* Madre
* Hijo
* Hija
* Encargado
* Cónyuge

**Importante:** estos son ejemplos de relaciones. Si en clase les dieron un catálogo específico, utiliza ese catálogo.

## Gestión de deudas

* Registro de deudas.
* Asociación de una deuda con un vecino.
* Consulta de deudas.
* Control del estado de la deuda.

## Gestión de multas

* Registro de multas.
* Asociación de multas con residentes.
* Consulta de multas.
* Control del estado de las multas.

## Gestión de usuarios

* Registro de usuarios.
* Modificación de usuarios.
* Activación/desactivación de usuarios.
* Control de acceso.

## Gestión de roles

* Creación de roles.
* Asociación de usuarios con roles.
* Control de funcionalidades disponibles según el rol.

# Actores del sistema

|  |  |
| --- | --- |
| Actor | Función |
| Administrador | Administra usuarios, roles y configuración general |
| Administrador de colonia | Gestiona casas, vecinos, familias, deudas y multas |
| Usuario de consulta | Consulta información permitida por su rol |

# Requerimientos funcionales

Aquí empiezas a convertir el proyecto en cosas que el sistema **debe poder hacer**.

**RF01. Gestión de casas**

El sistema deberá permitir registrar, consultar, modificar y gestionar las casas pertenecientes a la colonia.

**RF02. Gestión de vecinos**

El sistema deberá permitir registrar y administrar la información de los vecinos.

**RF03. Gestión de familias**

El sistema deberá permitir registrar familias y asociar sus integrantes.

**RF04. Gestión de hijos y encargados**

El sistema deberá permitir registrar hijos y encargados relacionados con una familia.

**RF05. Gestión de parentescos**

El sistema deberá permitir establecer relaciones de parentesco entre los integrantes de una familia.

**RF06. Gestión de deudas**

El sistema deberá permitir registrar y consultar las deudas asociadas individualmente a los residentes.

**RF07. Gestión de multas**

El sistema deberá permitir registrar y consultar multas asociadas a los residentes.

**RF08. Gestión de usuarios**

El sistema deberá permitir administrar las cuentas de usuario que tendrán acceso al sistema.

**RF09. Gestión de roles**

El sistema deberá permitir agrupar usuarios mediante roles.

**RF10. Control de acceso**

El sistema deberá restringir las funcionalidades de acuerdo con el rol asignado al usuario.

# Requerimientos no funcionales

Estos describen **cómo debe funcionar** el sistema.

**RNF01. Usabilidad**

La aplicación deberá contar con una interfaz sencilla y comprensible para los usuarios.

**RNF02. Seguridad**

El sistema deberá implementar autenticación y control de acceso basado en roles.

**RNF03. Disponibilidad**

La aplicación deberá estar disponible para los usuarios autorizados mediante un navegador web.

**RNF04. Mantenibilidad**

El código deberá organizarse de manera que facilite futuras modificaciones y ampliaciones.

**RNF05. Escalabilidad**

La estructura del sistema deberá permitir incorporar nuevas funcionalidades conforme evolucione el proyecto.

**RNF06. Integridad de datos**

La base de datos deberá utilizar relaciones y restricciones que permitan mantener la integridad de la información.

# Tecnologías seleccionadas

|  |  |
| --- | --- |
| Componente | Tecnología |
| Metodología | Scrum |
| Frontend | HTML, CSS y Bootstrap 5 |
| Backend | Python |
| Base de datos | PostgreSQL |
| Lenguaje principal | Python |
| Navegador | Google Chrome / Microsoft Edge / Firefox |
| Control de versiones | Git |
| Repositorio | GitHub |

# ¿Por qué utilizar estas herramientas?

## HTML, CSS y Bootstrap 5

Se utilizarán HTML, CSS y Bootstrap 5 para desarrollar la interfaz web del sistema. HTML permitirá estructurar el contenido de las diferentes páginas, CSS permitirá definir y personalizar los estilos visuales, mientras que Bootstrap 5 facilitará la creación de una interfaz responsiva y adaptable a diferentes tamaños de pantalla.

## Python

Se utilizará Python para implementar la lógica del sistema y desarrollar las funcionalidades necesarias para el procesamiento de la información. Su sintaxis sencilla y la disponibilidad de diferentes herramientas y bibliotecas facilitan el desarrollo de aplicaciones web.

## PostgreSQL

Se utilizará PostgreSQL como sistema gestor de base de datos debido a que es un sistema de gestión de bases de datos relacional que permite almacenar, organizar y consultar la información del sistema, además de establecer relaciones entre las diferentes entidades que lo conforman.

## Scrum

Se utilizará Scrum porque permite dividir el desarrollo en períodos de trabajo llamados **Sprints**, permitiendo desarrollar funcionalidades progresivamente, revisar los resultados y realizar ajustes conforme evoluciona el proyecto.

# Arquitectura propuesta

![](data:image/png;base64...)

# Diseño preliminar de la base de datos

**Casa**

* id\_casa
* numero
* estado

**Familia**

* id\_familia
* nombre

**Vecino**

* id\_vecino
* nombres
* apellidos
* telefono
* correo
* id\_casa
* id\_familia

**Parentesco**

* id\_parentesco
* nombre

**Vecino\_Parentesco**

* id\_vecino
* id\_relacionado
* id\_parentesco

**Deuda**

* id\_deuda
* id\_vecino
* concepto
* monto
* fecha
* estado

**Multa**

* id\_multa
* id\_vecino
* motivo
* monto
* fecha
* estado

**Rol**

* id\_rol
* nombre

**Usuario**

* id\_usuario
* usuario
* password
* id\_rol
* estado

# Módulos del sistema

![](data:image/png;base64...)

# Scrum aplicado al proyecto

## Roles Scrum

## Product Owner

Responsable de definir y priorizar las funcionalidades que necesita el sistema.

## Scrum Master

Responsable de facilitar la aplicación de Scrum y ayudar a resolver impedimentos.

## Equipo de desarrollo

Responsable del análisis, diseño, programación, pruebas y documentación del sistema.

# Product Backlog inicial

|  |  |  |
| --- | --- | --- |
| ID | Historia de usuario | Prioridad |
| HU01 | Como administrador quiero registrar casas para mantener el control de las viviendas. | Alta |
| HU02 | Como administrador quiero registrar vecinos para mantener actualizada la información residencial. | Alta |
| HU03 | Como administrador quiero registrar familias para organizar a los residentes. | Alta |
| HU04 | Como administrador quiero registrar relaciones de parentesco para conocer la relación entre integrantes. | Media |
| HU05 | Como administrador quiero registrar deudas para llevar control de los pagos pendientes. | Alta |
| HU06 | Como administrador quiero registrar multas para controlar las sanciones de los residentes. | Media |
| HU07 | Como administrador quiero registrar usuarios para controlar quién puede acceder al sistema. | Alta |
| HU08 | Como administrador quiero asignar roles a los usuarios para controlar sus permisos. | Alta |

# Sprints iniciales

## Sprint 1

**Base del sistema**

* Configuración del proyecto.
* Base de datos.
* Estructura inicial.
* Autenticación.
* Usuarios.
* Roles.

**Sprint 2**

**Gestión residencial**

* Casas.
* Vecinos.
* Familias.

## Sprint 3

**Relaciones familiares**

* Hijos.
* Encargados.
* Parentescos.

## Sprint 4

**Control financiero**

* Deudas.
* Estados de deuda.

## Sprint 5

**Control de multas**

* Registro de multas.
* Consulta.
* Estados.

## Sprint 6

**Finalización**

* Pruebas.
* Correcciones.
* Seguridad.
* Mejoras de interfaz.
* Documentación.