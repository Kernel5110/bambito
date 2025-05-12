# Panadería Bambi

![Logo de la Panadería Bambi](/imagenes/log.png)

Esta aplicación permite el control de ventas con un curioso diseño de interfaz hecho en `pygame` , gestión de inventarios, análisis de datos de desempeño y administración general de la Panadería ficticia **Bambi** a través de un sistema de punto de venta amigable, eficiente y confiable. Es solo un proyecto escolar por lo que no pretende brindar funcionalidades reales de un sistema punto de venta.

![](panbambi.png)

**Módulo de Inicio de Sesión (Login)**

Este módulo permite el acceso seguro al sistema mediante credenciales personalizadas para cada usuario. El login valida el nombre de usuario y contraseña, permitiendo así controlar el acceso a las diferentes áreas de la aplicación. Se pueden gestionar niveles de acceso dependiendo del rol del empleado.

**Módulo de Ventas**

Este módulo permite realizar ventas de productos de manera rápida y eficiente. El sistema registra cada venta y, al finalizar, genera y guarda automáticamente un ticket de compra en formato PDF. Además, facilita la búsqueda de productos y la asignación de clientes a las ventas.

**Módulo de Almacén**

Este módulo muestra en tiempo real el inventario de insumos y materias primas disponibles en el almacén. Los usuarios pueden consultar cantidades actuales, realizar ajustes de stock y registrar nuevas entradas de productos para mantener actualizado el inventario.

**Módulo de Reportes**

Este módulo ofrece gráficos y reportes que permiten analizar el rendimiento de la panadería. Se pueden visualizar datos como las ventas realizadas durante la semana, los productos más vendidos (por ejemplo, qué tipos de pan), y los horarios de mayor venta. Esta información ayuda en la toma de decisiones estratégicas.

**Módulo de Ajustes**

Este módulo permite configurar aspectos esenciales de la aplicación, como cambiar el logo de la panadería, agregar nuevos empleados, registrar proveedores y clientes, así como modificar información general del sistema. Ofrece flexibilidad para adaptar el sistema a las necesidades de la empresa.

### **Dependencias**

- pygame
- tkinter
- mysql
- icecream
- smtplib
- requests
- reportlab
- fpdf
