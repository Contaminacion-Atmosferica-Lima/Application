# Lima AirGraph – Visualización y Algoritmos de Redes de Contaminación del Aire

Este proyecto analiza y visualiza la red de contaminación del aire en Lima Metropolitana usando datos reales de SENAMHI (2015–2024).  
Incluye un backend en **Flask** y dos interfaces visuales:

- **Mapa interactivo (Leaflet)** para grafos diarios.  
- **Visualizador global por distrito (Cytoscape)** para examinar la evolución temporal de un distrito.

También implementa algoritmos enseñados en el curso de Complejidad Algorítmica:

- **BFS**
- **Union-Find (UFDS)**
- **MST**
- **Graph Builder**

---

## Requisitos

- Python **3.10–3.12**  
- Pip actualizado  
- Virtualenv recomendado  

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Contaminacion-Atmosferica-Lima/Application.git
```

### 2. Crear entorno virtual
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

## Ejecutar el backend
```bash
python app.py
```

El servidor estará disponible en:
```bash
http://127.0.0.1:5000
```
La documentación Swagger:
```bash
http://127.0.0.1:5000/apidocs
```