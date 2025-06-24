from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import re
import time
from datetime import datetime, timedelta
import random
import hashlib

# Importar la base de conocimientos
from .knowledge_base import (
    PRODUCTOS, 
    SERVICIOS, 
    POLITICAS, 
    DESCUENTOS, 
    CONTACTO, 
    PREGUNTAS_FRECUENTES,
    TERMINOLOGIA,
    EMPRESA
)

# Diccionario de respuestas en caché para optimizar el rendimiento
response_cache = {}

# Caché con tiempo de expiración (24 horas)
response_cache_with_expiry = {}

# Contador de preguntas frecuentes para personalización
question_frequency = {}

# Contexto de conversación para respuestas más naturales
conversation_context = {}

# Sistema de respuestas inteligentes basado en base de conocimientos
def get_ai_response(query, user_id=None):
    """
    Genera respuestas basadas en la base de conocimientos estructurada.
    Utiliza patrones de reconocimiento y contexto de conversación para personalizar las respuestas.
    """
    query_lower = query.lower().strip()
    
    # Generar un ID de usuario si no se proporciona para seguimiento de conversaciones
    if not user_id:
        user_id = "anonymous_user"
        
    # Verificar si la respuesta está en caché con tiempo de expiración
    current_time = datetime.now()
    cache_key = f"{user_id}_{query_lower}"
    
    if cache_key in response_cache_with_expiry:
        cached_time, cached_response = response_cache_with_expiry[cache_key]
        # Verificar si la caché sigue siendo válida (menos de 24 horas)
        if current_time - cached_time < timedelta(hours=24):
            return cached_response
    
    # Verificar si la respuesta está en caché permanente
    if query_lower in response_cache:
        return response_cache[query_lower]
    
    # Registrar frecuencia de pregunta para personalización
    if query_lower not in question_frequency:
        question_frequency[query_lower] = 0
    question_frequency[query_lower] += 1
    
    # Registrar contexto de conversación
    if user_id not in conversation_context:
        conversation_context[user_id] = {
            'last_query_time': current_time,
            'query_history': [],
            'total_queries': 0,
            'common_topics': set()
        }
    
    # Actualizar contexto del usuario
    context = conversation_context[user_id]
    context['last_query_time'] = current_time
    context['query_history'].append(query_lower)
    context['total_queries'] += 1
    
    # Limitar historial a las últimas 10 consultas
    if len(context['query_history']) > 10:
        context['query_history'] = context['query_history'][-10:]
    
    # Actualizar temas comunes basados en la terminología definida
    for category, terms in TERMINOLOGIA.items():
        for term in terms:
            if term in query_lower:
                context['common_topics'].add(category)
                break
    
    # Función para detectar si un término de una categoría está en la consulta
    def contains_terms(category_key):
        terms = TERMINOLOGIA.get(category_key, [])
        return any(term in query_lower for term in terms)

    # Base de conocimiento más extensa y personalizada
    if re.search(r'\b(hola|saludos|buenos días|buenas tardes|buenas noches)\b', query_lower):
        # Personalizar saludo según hora del día
        hour = datetime.now().hour
        greeting = "Buenos días" if 5 <= hour < 12 else "Buenas tardes" if 12 <= hour < 19 else "Buenas noches"
        
        # Personalizar según historial de conversación
        if context['total_queries'] > 1:
            response = f"¡{greeting}! Bienvenido de nuevo al asistente virtual de MultiAndamios. "
            
            # Si ha preguntado por temas específicos antes, mencionarlos
            if context['common_topics']:
                topics = list(context['common_topics'])
                if len(topics) == 1:
                    response += f"Veo que antes estabas interesado en {topics[0]}. ¿Puedo ayudarte con algo más sobre ese tema?"
                else:
                    topic_str = ", ".join(topics[:-1]) + " y " + topics[-1]
                    response += f"Veo que te has interesado en {topic_str}. ¿En qué puedo ayudarte hoy?"
            else:
                response += "¿En qué puedo asistirte en esta ocasión?"
        else:
            response = f"¡{greeting}! Soy el asistente virtual de {EMPRESA['nombre']}. Estoy aquí para ayudarte con información sobre nuestros productos, servicios y procesos de alquiler. ¿En qué puedo asistirte hoy?"    # Consultas sobre andamios
    elif contains_terms("andamios"):
        if re.search(r'\b(tipo|tipos|clase|clases|diferentes|opciones|cuáles|cuales)\b', query_lower):
            # Construir respuesta detallada basada en la base de conocimientos
            andamios_info = PRODUCTOS['andamios']['tipos']
            response = "Ofrecemos varios tipos de andamios para diferentes necesidades:\n\n"
            
            for andamio in andamios_info:
                response += f"• **{andamio['nombre']}**: {andamio['descripcion']} {andamio['usos']}\n"
                
            response += "\nTodos nuestros andamios cumplen con certificaciones internacionales como " + ", ".join(PRODUCTOS['andamios']['certificaciones'][:2]) + "."
            response += "\n\n¿Te gustaría información más detallada sobre algún tipo específico de andamio?"
            
        elif re.search(r'\b(precio|costo|tarifa|valor|cuánto cuesta|cuanto vale)\b', query_lower):
            # Información de precios desde la base de conocimientos
            andamios_info = PRODUCTOS['andamios']['tipos']
            response = "Los precios de nuestros andamios varían según el tipo, cantidad y tiempo de alquiler:\n\n"
            
            for andamio in andamios_info:
                response += f"• **{andamio['nombre']}**: ${andamio['precio_diario']} por día, ${andamio['precio_semanal']} por semana, ${andamio['precio_mensual']} por mes.\n"
            
            response += "\nOfrecemos descuentos por volumen y duración del alquiler. Para alquileres de más de 3 meses, puedes obtener hasta un " + DESCUENTOS['duracion'][-1]['porcentaje'] + " de descuento."
            response += "\n\n¿Necesitas una cotización personalizada para tu proyecto?"
            
        elif re.search(r'\b(disponibilidad|disponible|tienen|hay|inventario|stock)\b', query_lower):
            # Información de disponibilidad
            andamios_info = PRODUCTOS['andamios']['tipos']
            response = "Actualmente contamos con la siguiente disponibilidad de andamios:\n\n"
            
            for andamio in andamios_info:
                response += f"• **{andamio['nombre']}**: {andamio['disponibilidad']}\n"
                
            response += "\nRecomendamos reservar con anticipación para garantizar la disponibilidad, especialmente para proyectos grandes o en temporada alta de construcción."
            
        elif re.search(r'\b(certificación|certificado|seguridad|norma|normas)\b', query_lower):
            # Información de certificaciones
            response = "Todos nuestros andamios cuentan con las siguientes certificaciones:\n\n"
            for cert in PRODUCTOS['andamios']['certificaciones']:
                response += f"• {cert}\n"
            
            response += "\nLa seguridad es nuestra prioridad, por eso todos nuestros equipos son inspeccionados rigurosamente antes de cada alquiler."
            
        elif re.search(r'\b(accesorios|complementos|adicional)\b', query_lower):
            # Información de accesorios
            accesorios = PRODUCTOS['andamios']['accesorios']
            response = "Complementamos nuestros andamios con los siguientes accesorios:\n\n"
            
            for accesorio in accesorios:
                response += f"• **{accesorio['nombre']}**: ${accesorio['precio_semanal']} por semana. Disponibilidad: {accesorio['disponibilidad']}\n"
            
            response += "\nTodos estos accesorios están diseñados para aumentar la seguridad y funcionalidad de nuestros andamios."
            
        else:
            response = f"En {EMPRESA['nombre']} contamos con varios tipos de andamios certificados para diferentes necesidades, incluyendo andamios multidireccionales, andamios de marco, torres móviles y andamios colgantes. Todos están fabricados con materiales de alta calidad y cumplen con los estándares internacionales de seguridad.\n\n¿Te gustaría información sobre algún tipo específico, precios, disponibilidad o accesorios?"
            
    elif contains_terms("formaletas"):
        if re.search(r'\b(columna|columnas)\b', query_lower):
            # Obtener información específica de formaletas para columnas
            formaleta_columnas = next((f for f in PRODUCTOS['formaletas']['tipos'] if "Columnas" in f['nombre']), None)
            
            if formaleta_columnas:
                response = f"**{formaleta_columnas['nombre']}**\n\n{formaleta_columnas['descripcion']}\n\n"
                response += f"**Especificaciones técnicas**: {formaleta_columnas['especificaciones']}\n\n"
                response += f"**Usos recomendados**: {formaleta_columnas['usos']}\n\n"
                response += f"**Precios**: ${formaleta_columnas['precio_diario']} por día, ${formaleta_columnas['precio_semanal']} por semana, ${formaleta_columnas['precio_mensual']} por mes.\n\n"
                response += f"**Disponibilidad actual**: {formaleta_columnas['disponibilidad']}"
            else:
                response = "Nuestras formaletas para columnas están disponibles en diferentes tamaños y formas (circulares, cuadradas y rectangulares). Son modulares, fáciles de instalar y ofrecen un excelente acabado superficial del concreto. Ideales para proyectos residenciales y comerciales."
            
        elif re.search(r'\b(muro|muros|pared|paredes)\b', query_lower):
            # Obtener información específica de formaletas para muros
            formaleta_muros = next((f for f in PRODUCTOS['formaletas']['tipos'] if "Muros" in f['nombre']), None)
            
            if formaleta_muros:
                response = f"**{formaleta_muros['nombre']}**\n\n{formaleta_muros['descripcion']}\n\n"
                response += f"**Especificaciones técnicas**: {formaleta_muros['especificaciones']}\n\n"
                response += f"**Usos recomendados**: {formaleta_muros['usos']}\n\n"
                response += f"**Precios**: ${formaleta_muros['precio_diario']} por día, ${formaleta_muros['precio_semanal']} por semana, ${formaleta_muros['precio_mensual']} por mes.\n\n"
                response += f"**Disponibilidad actual**: {formaleta_muros['disponibilidad']}"
            else:
                response = "Las formaletas para muros que ofrecemos son ligeras pero resistentes, con sistemas de anclaje rápido que reducen el tiempo de instalación. Disponibles en diferentes dimensiones para adaptarse a cualquier proyecto."
                
        elif re.search(r'\b(losa|losas|techo|techos)\b', query_lower):
            # Obtener información específica de formaletas para losas
            formaleta_losas = next((f for f in PRODUCTOS['formaletas']['tipos'] if "Losas" in f['nombre']), None)
            
            if formaleta_losas:
                response = f"**{formaleta_losas['nombre']}**\n\n{formaleta_losas['descripcion']}\n\n"
                response += f"**Especificaciones técnicas**: {formaleta_losas['especificaciones']}\n\n"
                response += f"**Usos recomendados**: {formaleta_losas['usos']}\n\n"
                response += f"**Precios**: ${formaleta_losas['precio_diario']} por día, ${formaleta_losas['precio_semanal']} por semana, ${formaleta_losas['precio_mensual']} por mes.\n\n"
                response += f"**Disponibilidad actual**: {formaleta_losas['disponibilidad']}"
            else:
                response = "Contamos con sistemas de encofrado para losas que incluyen puntales, vigas y tableros. Son ajustables en altura y permiten una distribución uniforme de cargas. Ideales para construcción de pisos y techos."
        
        elif re.search(r'\b(precio|costo|tarifa|valor|cuánto cuesta|cuanto vale)\b', query_lower):
            # Información de precios de todas las formaletas
            formaletas_info = PRODUCTOS['formaletas']['tipos']
            response = "Los precios de nuestras formaletas varían según el tipo y tiempo de alquiler:\n\n"
            
            for formaleta in formaletas_info:
                response += f"• **{formaleta['nombre']}**: ${formaleta['precio_diario']} por día, ${formaleta['precio_semanal']} por semana, ${formaleta['precio_mensual']} por mes.\n"
            
            response += "\nTambién ofrecemos descuentos por volumen y duración del alquiler. Para proyectos grandes, consulta nuestras ofertas especiales."
            
        elif re.search(r'\b(accesorios|complementos|adicional)\b', query_lower):
            # Información de accesorios para formaletas
            accesorios = PRODUCTOS['formaletas']['accesorios']
            response = "Disponemos de los siguientes accesorios para complementar nuestras formaletas:\n\n"
            
            for accesorio in accesorios:
                if 'precio_semanal' in accesorio:
                    response += f"• **{accesorio['nombre']}**: ${accesorio['precio_semanal']} por semana. Disponibilidad: {accesorio['disponibilidad']}\n"
                else:
                    response += f"• **{accesorio['nombre']}**: ${accesorio['precio_por_galon']} por galón. Disponibilidad: {accesorio['disponibilidad']}\n"
                    
            response += "\nEstos accesorios son esenciales para un correcto montaje y desmontaje de las formaletas."
            
        else:
            # Respuesta general sobre formaletas
            response = "Nuestras formaletas son ideales para estructuras de concreto. Ofrecemos sistemas para:\n\n"
            
            for formaleta in PRODUCTOS['formaletas']['tipos']:
                response += f"• **{formaleta['nombre']}**: {formaleta['descripcion'][:50]}...\n"
                
            response += "\nTodas nuestras formaletas son modulares, duraderas y fáciles de ensamblar. Fabricadas con materiales de alta resistencia que garantizan acabados de calidad en el concreto."
            response += "\n\n¿Necesitas información sobre algún tipo específico de formaleta, precios o accesorios disponibles?"
            
    elif contains_terms("precio") and not (contains_terms("andamios") or contains_terms("formaletas")):
        if re.search(r'\b(lista|catálogo|completo|todos|general)\b', query_lower):
            # Lista completa de precios
            response = "A continuación te presento un resumen de nuestros precios:\n\n"
            response += "**ANDAMIOS**\n"
            for andamio in PRODUCTOS['andamios']['tipos']:
                response += f"• {andamio['nombre']}: ${andamio['precio_diario']} por día, ${andamio['precio_semanal']} por semana, ${andamio['precio_mensual']} por mes.\n"
                
            response += "\n**FORMALETAS**\n"
            for formaleta in PRODUCTOS['formaletas']['tipos']:
                response += f"• {formaleta['nombre']}: ${formaleta['precio_diario']} por día, ${formaleta['precio_semanal']} por semana, ${formaleta['precio_mensual']} por mes.\n"
                
            response += "\nPara una cotización personalizada, puedes visitar nuestro catálogo completo con precios en la sección de Productos de nuestra web. También podemos enviarte una cotización detallada por correo electrónico. ¿Te gustaría proporcionarnos tu correo para enviarte el catálogo completo?"
            
        elif re.search(r'\b(descuento|descuentos|promoción|promociones|rebaja|rebajas|oferta|ofertas)\b', query_lower):
            # Información sobre descuentos
            response = "En MultiAndamios ofrecemos diversos descuentos:\n\n"
            
            response += "**Descuentos por Volumen:**\n"
            for desc in DESCUENTOS['volumen']:
                response += f"• Alquileres entre {desc['rango']}: {desc['porcentaje']} de descuento\n"
                
            response += "\n**Descuentos por Duración:**\n"
            for desc in DESCUENTOS['duracion']:
                response += f"• Alquileres de {desc['periodo']}: {desc['porcentaje']} de descuento\n"
                
            response += f"\n**Programa de Cliente Frecuente:**\n"
            response += f"• {DESCUENTOS['cliente_frecuente']['criterio']}: {DESCUENTOS['cliente_frecuente']['beneficio']}\n"
            
            response += f"\nTambién ofrecemos {DESCUENTOS['proyectos_especiales']}"
            
        else:
            # Respuesta general sobre precios
            response = "Nuestros precios varían según el tipo de equipo, cantidad y duración del alquiler:\n\n"
            
            # Obtener rangos de precios
            andamios_min_precio = min([a['precio_semanal'] for a in PRODUCTOS['andamios']['tipos']])
            andamios_max_precio = max([a['precio_semanal'] for a in PRODUCTOS['andamios']['tipos']])
            
            formaletas_min_precio = min([f['precio_semanal'] for f in PRODUCTOS['formaletas']['tipos']])
            formaletas_max_precio = max([f['precio_semanal'] for f in PRODUCTOS['formaletas']['tipos']])
            
            response += f"• Andamios: ${andamios_min_precio} - ${andamios_max_precio} por semana\n"
            response += f"• Formaletas: ${formaletas_min_precio} - ${formaletas_max_precio} por semana\n\n"
            
            response += "Los precios incluyen mantenimiento básico y garantía durante el alquiler. También ofrecemos descuentos por volumen y duración.\n\n"
            response += "Para darte un precio exacto, necesitaría conocer los detalles específicos de tu proyecto. ¿Puedes proporcionarnos más información sobre lo que necesitas o prefieres que un asesor te contacte?"
    elif contains_terms("alquiler"):
        if re.search(r'\b(proceso|cómo|como|requisitos|pasos)\b', query_lower):
            # Proceso de alquiler desde la base de conocimientos
            pasos = SERVICIOS['alquiler']['proceso']
            requisitos = SERVICIOS['alquiler']['requisitos']
            
            response = "El proceso de alquiler es muy sencillo:\n\n"
            for i, paso in enumerate(pasos, 1):
                response += f"{i}️⃣ {paso}\n"
                
            response += "\n**Requisitos:**\n"
            for requisito in requisitos:
                response += f"• {requisito}\n"
                
            response += "\nSi prefieres, también puedes hacer tu solicitud por teléfono al " + CONTACTO['telefono'] + " o visitar nuestras instalaciones en " + CONTACTO['direccion'] + "."
            
        elif re.search(r'\b(requisito|necesito|documentos|documento)\b', query_lower):
            # Requisitos específicos
            requisitos = SERVICIOS['alquiler']['requisitos']
            response = "Para alquilar nuestros equipos necesitarás:\n\n"
            
            for requisito in requisitos:
                response += f"• {requisito}\n"
                
            response += "\nSi representas a una empresa, también necesitarás una copia reciente del certificado de Cámara de Comercio."
            
        elif re.search(r'\b(ventaja|ventajas|beneficio|beneficios)\b', query_lower):
            # Ventajas del alquiler
            ventajas = SERVICIOS['alquiler']['ventajas']
            response = "Alquilar con nosotros tiene múltiples ventajas:\n\n"
            
            for ventaja in ventajas:
                response += f"• {ventaja}\n"
                
            response += "\nAdemás, contamos con asesoría técnica personalizada durante todo el período de alquiler."
            
        elif re.search(r'\b(mínimo|minimo|menor|corto)\b', query_lower):
            # Tiempo mínimo de alquiler
            for faq in PREGUNTAS_FRECUENTES:
                if "tiempo mínimo de alquiler" in faq['pregunta'].lower():
                    response = faq['respuesta']
                    break
            else:
                response = "El tiempo mínimo de alquiler para la mayoría de nuestros equipos es de una semana. Sin embargo, para ciertos equipos especializados ofrecemos alquileres por día con una tarifa diferenciada."
            
        else:
            # Respuesta general sobre alquiler
            response = f"Alquilar con {EMPRESA['nombre']} es fácil y flexible. Ofrecemos contratos semanales, mensuales o personalizados según tus necesidades. El proceso incluye seleccionar los productos, especificar la duración, completar el pago y coordinar la entrega.\n\n"
            response += "Algunas ventajas de nuestro servicio de alquiler:\n"
            for ventaja in SERVICIOS['alquiler']['ventajas'][:3]:  # Mostrar solo las primeras 3 ventajas
                response += f"• {ventaja}\n"
                
            response += "\n¿Te gustaría comenzar un alquiler ahora o necesitas más información específica sobre el proceso, requisitos o ventajas?"
            
    elif contains_terms("entrega"):
        if re.search(r'\b(tiempo|plazo|cuando|cuándo|cuanto|cuánto|demora|rápido)\b', query_lower):
            # Tiempos de entrega
            zonas = SERVICIOS['transporte']['zonas']
            response = "Nuestros tiempos de entrega estándar son:\n\n"
            
            for zona, info in zonas.items():
                if zona == "urbana":
                    zona_nombre = "Dentro de la ciudad"
                elif zona == "metropolitana":
                    zona_nombre = "Áreas metropolitanas"
                elif zona == "regional":
                    zona_nombre = "Zonas rurales o alejadas"
                else:
                    zona_nombre = "Resto del país"
                
                response += f"• {zona_nombre}: {info['tiempo_entrega']}\n"
                
            # Servicio express
            express = next((s for s in SERVICIOS['transporte']['servicios_adicionales'] if s['nombre'] == "Entrega Express"), None)
            if express:
                response += f"\nPara pedidos urgentes, contamos con servicio express: {express['descripcion']} (sobrecosto de {express['sobrecosto']})."
                
            response += "\n\n¿Necesitas una entrega con urgencia o tienes una fecha específica para tu proyecto?"
                
        elif re.search(r'\b(costo|precio|tarifa|valor|cobran)\b', query_lower):
            # Costos de entrega
            zonas = SERVICIOS['transporte']['zonas']
            response = "El costo de entrega depende de la distancia y volumen del pedido:\n\n"
            
            for zona, info in zonas.items():
                if zona == "urbana":
                    zona_nombre = "Zona urbana"
                elif zona == "metropolitana":
                    zona_nombre = "Zona metropolitana"
                elif zona == "regional":
                    zona_nombre = "Fuera de la ciudad"
                else:
                    zona_nombre = "Nacional"
                
                if 'costo_base' in info:
                    response += f"• {zona_nombre}: desde ${info['costo_base']}"
                    if 'costo_adicional' in info:
                        response += f" ({info['costo_adicional']})"
                    response += "\n"
                else:
                    response += f"• {zona_nombre}: {info['costo']}\n"
                    
            response += "\nPara pedidos grandes, ofrecemos tarifas especiales de entrega. ¿En qué zona se ubicaría tu proyecto?"
            
        elif re.search(r'\b(servicio adicional|montaje|desmontaje|instalación|supervisión)\b', query_lower):
            # Servicios adicionales de transporte
            servicios = SERVICIOS['transporte']['servicios_adicionales']
            response = "Además del transporte básico, ofrecemos los siguientes servicios adicionales:\n\n"
            
            for servicio in servicios:
                response += f"• **{servicio['nombre']}**: {servicio['descripcion']}. Costo: {servicio['costo'] if 'costo' in servicio else servicio['sobrecosto']}\n"
                
            response += "\nEstos servicios pueden contratarse al momento de realizar tu pedido. ¿Te gustaría añadir alguno de estos servicios a tu alquiler?"
            
        else:
            # Respuesta general sobre entregas
            response = f"En {EMPRESA['nombre']} ofrecemos servicio completo de logística, incluyendo entrega y recogida en cualquier ubicación. Nuestro equipo coordina todo el proceso logístico, desde la carga hasta la descarga en el sitio de obra.\n\n"
            
            response += "**Cobertura de entregas:**\n"
            for zona, info in SERVICIOS['transporte']['zonas'].items():
                if zona == "urbana":
                    zona_nombre = "Zona urbana"
                elif zona == "metropolitana":
                    zona_nombre = "Zona metropolitana"
                elif zona == "regional":
                    zona_nombre = "Regional"
                else:
                    zona_nombre = "Nacional"
                
                response += f"• {zona_nombre}: Tiempo de entrega {info['tiempo_entrega']}\n"
                
            response += "\nTambién contamos con servicio express para necesidades urgentes y personal especializado para montaje y desmontaje. ¿Necesitas información más específica sobre tiempos, costos o servicios adicionales de entrega?"
    elif contains_terms("seguridad"):
        if re.search(r'\b(certificados|certificaciones|comprobante|normativas|normas)\b', query_lower):
            # Información de certificaciones
            normas = POLITICAS['seguridad']['normas_cumplimiento']
            response = "Todos nuestros equipos cumplen con las siguientes certificaciones y normativas de seguridad:\n\n"
            
            for norma in normas:
                response += f"• {norma}\n"
                
            # Añadir certificaciones específicas de productos
            response += "\n**Certificaciones específicas de andamios:**\n"
            for cert in PRODUCTOS['andamios']['certificaciones']:
                response += f"• {cert}\n"
                
            response += "\nProporcionamos los certificados de calidad y seguridad junto con cada alquiler para tu tranquilidad y cumplimiento normativo."
            
        elif re.search(r'\b(accidente|caída|caídas|accidentes|responsabilidad|prevención|riesgo)\b', query_lower):
            # Información sobre prevención de accidentes
            response = "La seguridad es nuestra máxima prioridad. Para prevenir accidentes:\n\n"
            response += "• Todos nuestros equipos incluyen sistemas anti-caídas y componentes de seguridad.\n"
            response += "• Realizamos inspecciones técnicas exhaustivas antes de cada alquiler.\n"
            response += f"• Ofrecemos {POLITICAS['seguridad']['capacitacion']['incluida']}.\n"
            response += f"• También disponemos de {POLITICAS['seguridad']['capacitacion']['adicional']}.\n"
            response += "• Incluimos un seguro de responsabilidad civil básico con cada alquiler.\n\n"
            response += "Recomendamos verificar que tu póliza de obra cubra adecuadamente el uso de andamios y equipos en altura."
            
        elif re.search(r'\b(capacitación|capacitacion|entrenamiento|formación|formar|curso|cursos)\b', query_lower):
            # Información sobre capacitación
            response = f"Ofrecemos los siguientes servicios de capacitación en seguridad:\n\n"
            response += f"• **Capacitación básica**: {POLITICAS['seguridad']['capacitacion']['incluida']}. Esta capacitación está incluida con cada alquiler y cubre montaje seguro, uso adecuado y desmontaje.\n\n"
            response += f"• **Capacitación avanzada**: {POLITICAS['seguridad']['capacitacion']['adicional']}. Este curso cumple con los requisitos legales para trabajo en alturas y proporciona certificación oficial.\n\n"
            response += "Nuestros instructores son profesionales certificados con amplia experiencia en el sector."
            
        else:
            # Respuesta general sobre seguridad
            response = f"La seguridad es el núcleo del negocio de {EMPRESA['nombre']}. Todos nuestros equipos:\n\n"
            response += "• Cumplen con normas internacionales de seguridad\n"
            response += f"• Son sometidos a {POLITICAS['seguridad']['inspeccion']} para garantizar su estado óptimo\n"
            response += "• Incluyen componentes de seguridad como barandillas, rodapiés y sistemas de anclaje\n"
            response += "• Vienen con manuales detallados de montaje y uso seguro\n\n"
            response += f"Además, ofrecemos {POLITICAS['seguridad']['capacitacion']['incluida']} sin costo adicional, y nuestro equipo técnico puede realizar visitas para verificar el montaje correcto.\n\n"
            response += "¿Tienes alguna preocupación específica sobre seguridad que podamos abordar?"
    elif re.search(r'\b(pago|pagar|efectivo|tarjeta|transferencia|depósito|crédito|factura|facturación)\b', query_lower):
        if re.search(r'\b(método|métodos|forma|formas|opciones)\b', query_lower):
            # Métodos de pago desde la base de conocimientos
            metodos = POLITICAS['pago']['metodos_aceptados']
            response = "Aceptamos diversas formas de pago para tu comodidad:\n\n"
            for metodo in metodos:
                response += f"• {metodo}\n"
                
            response += "\n¿Qué método de pago preferirías utilizar?"
            
        elif re.search(r'\b(depósito|garantía|seguridad|fianza)\b', query_lower):
            # Información sobre depósito
            deposito = POLITICAS['pago']['deposito_seguridad']
            response = f"Para alquileres, solicitamos un depósito de seguridad reembolsable {deposito['porcentaje']} del valor total del alquiler.\n\n"
            response += f"Este depósito se devuelve {deposito['devolucion']}."
            
            # Complementar con FAQs
            for faq in PREGUNTAS_FRECUENTES:
                if "depósito de seguridad" in faq['pregunta'].lower():
                    response += f"\n\n**Pregunta frecuente**: {faq['pregunta']}\n{faq['respuesta']}"
                    break
            
        elif re.search(r'\b(factura|facturación|electrónica|contabilidad|comprobante)\b', query_lower):
            # Información sobre facturación
            facturacion = POLITICAS['pago']['facturacion']
            response = f"Nuestra facturación es de tipo {facturacion['tipo']}. Para emitir facturas necesitamos los siguientes datos:\n\n"
            response += f"• {facturacion['datos_requeridos']}\n\n"
            response += "Todas nuestras facturas cumplen con los requisitos fiscales vigentes y son enviadas automáticamente al correo electrónico registrado."
            
        else:
            # Respuesta general sobre pagos
            response = "Ofrecemos múltiples opciones de pago para adaptarnos a tus necesidades:\n\n"
            for metodo in POLITICAS['pago']['metodos_aceptados'][:3]:  # Mostrar solo los primeros métodos
                response += f"• {metodo}\n"
                
            response += f"\nPara empresas y proyectos grandes, contamos con planes de crédito y facilidades de pago. "
            response += f"Se requiere un depósito de seguridad reembolsable ({POLITICAS['pago']['deposito_seguridad']['porcentaje']} del valor) que se devuelve al finalizar el alquiler. "
            response += f"Emitimos {POLITICAS['pago']['facturacion']['tipo']} con todos los detalles para tu contabilidad.\n\n"
            response += "¿Necesitas información sobre alguna forma de pago específica?"
    elif re.search(r'\b(garantía|garantías|problema|daño|reemplazo|falla|reparación|mal funcionamiento|defecto)\b', query_lower):
        # Información sobre garantía
        cobertura = POLITICAS['garantia']['cobertura']
        exclusiones = POLITICAS['garantia']['exclusiones']
        procedimiento = POLITICAS['garantia']['procedimiento']
        
        response = f"Todos nuestros equipos tienen garantía completa durante el período de alquiler.\n\n"
        response += f"**La garantía cubre**: {cobertura}\n\n"
        response += f"**No incluye**: {exclusiones}\n\n"
        response += f"**En caso de problema**: {procedimiento}\n\n"
        
        # Añadir información de preguntas frecuentes
        for faq in PREGUNTAS_FRECUENTES:
            if "servicio técnico" in faq['pregunta'].lower():
                response += f"**Soporte técnico**: {faq['respuesta']}\n\n"
                break
                
        response += "El depósito de seguridad solo se aplica a daños por mal uso, no por desgaste normal o fallas técnicas. También ofrecemos extensiones de garantía para alquileres de larga duración.\n\n"
        response += "¿Tienes alguna preocupación específica sobre nuestra política de garantía?"
    elif re.search(r'\b(contacto|teléfono|email|correo|asesor|representante|comunicar|comunicación|whatsapp)\b', query_lower):
        if re.search(r'\b(asesor|representante|vendedor|técnico|especialista)\b', query_lower):
            response = "Podemos asignarte un asesor técnico especializado que te acompañará durante todo el proceso. Por favor, indícame tu nombre, teléfono y el mejor horario para contactarte, y nuestro equipo se comunicará contigo dentro de las próximas 4 horas hábiles."
        else:
            # Información de contacto desde la base de conocimientos
            response = f"Estamos disponibles a través de múltiples canales:\n\n"
            response += f"• Teléfono: {CONTACTO['telefono']} (Horario: {CONTACTO['horario']['lunes_viernes']} L-V, {CONTACTO['horario']['sabado']} Sáb)\n"
            response += f"• WhatsApp: {CONTACTO['whatsapp']} (atención 24/7)\n"
            response += f"• Email: {CONTACTO['email']}\n"
            response += f"• Website: {CONTACTO['website']}\n"
            response += f"• Oficinas: {CONTACTO['direccion']}\n\n"
            response += "También podemos asignarte un asesor personalizado para tu proyecto. ¿Cómo prefieres que te contactemos?"
    
    elif re.search(r'\b(gracias|agradecido|gracias|agradezco|thanks)\b', query_lower):
        response = "¡Ha sido un placer ayudarte! Estamos para servirte en cualquier momento. Si tienes más preguntas o necesitas asistencia adicional, no dudes en escribirme. ¿Hay algo más en lo que pueda orientarte hoy?"
    
    elif re.search(r'\b(proyecto|proyectos|obra|obras|construcción)\b', query_lower):
        response = "Para proyectos de construcción, ofrecemos soluciones integrales que incluyen asesoría técnica, planificación logística, y equipamiento completo. Nuestro equipo técnico puede realizar una visita a tu obra para evaluar las necesidades específicas y proponer la mejor combinación de equipos. También ofrecemos descuentos para proyectos grandes o de larga duración. ¿Te gustaría que un especialista evalúe tu proyecto?"
    
    elif re.search(r'\b(descuento|descuentos|promoción|promociones|oferta|ofertas|rebaja|rebajas)\b', query_lower):
        response = "Contamos con varios programas de descuentos:\n\n• Descuentos por volumen: 5-15% según cantidad\n• Descuentos por duración: 10-20% para alquileres >1 mes\n• Programa de cliente frecuente: hasta 25% de descuento\n• Promociones estacionales: Consulta nuestras ofertas actuales\n\nAdemás, ofrecemos tarifas especiales para constructoras y contratistas registrados. ¿Te gustaría conocer qué descuento aplicaría para tu caso específico?"
      # Inteligencia artificial y chat
    elif re.search(r'\b(inteligente|inteligencia|artificial|ai|ia|robot|chatbot|bot)\b', query_lower):
        response = "Soy un asistente virtual de MultiAndamios, diseñado para brindar información rápida y precisa sobre nuestros productos y servicios. Aunque utilizo tecnología para entender tus preguntas, siempre tienes la opción de hablar con un asesor humano en cualquier momento. ¿Te gustaría que te ponga en contacto con un miembro de nuestro equipo?"
    
    # Nuevo caso: Disponibilidad
    elif re.search(r'\b(disponible|disponibilidad|stock|inventario|hay|tienen|existencia|existencias)\b', query_lower):
        response = "Mantenemos un amplio inventario de equipos para satisfacer la demanda. La disponibilidad específica puede variar según la temporada y los proyectos activos. Te recomendamos reservar con antelación, especialmente para cantidades grandes o proyectos de larga duración. Podemos verificar la disponibilidad exacta de los productos que necesitas en tiempo real. ¿Qué equipos específicos te interesan?"
    
    # Nuevo caso: Experiencia o historial
    elif re.search(r'\b(experiencia|años|trayectoria|historia|reputación|confianza|cliente|clientes)\b', query_lower):
        response = "MultiAndamios cuenta con más de 15 años de experiencia en el sector de la construcción. Hemos participado en proyectos de todo tipo y escala, desde pequeñas reformas hasta grandes desarrollos urbanos e infraestructuras. Nos respaldan más de 1,000 clientes satisfechos, incluyendo las principales constructoras del país. Nuestro compromiso con la calidad y la seguridad nos ha posicionado como líderes en el sector de alquiler de andamios y formaletas."
      # Buscar si la consulta coincide con alguna pregunta frecuente
    elif any(re.search(re.escape(faq['pregunta'].lower()), query_lower) for faq in PREGUNTAS_FRECUENTES):
        for faq in PREGUNTAS_FRECUENTES:
            if re.search(re.escape(faq['pregunta'].lower()), query_lower):
                response = faq['respuesta']
                break
    
    # Buscar información sobre la empresa
    elif re.search(r'\b(empresa|compañía|sobre ustedes|historia|años|experiencia|multiandamios)\b', query_lower):
        response = f"**{EMPRESA['nombre']}** es una empresa fundada en {EMPRESA['fundacion']}, con más de {datetime.now().year - EMPRESA['fundacion']} años de experiencia en el sector.\n\n"
        response += f"**Nuestra misión**: {EMPRESA['mision']}\n\n"
        response += f"**Nuestra visión**: {EMPRESA['vision']}\n\n"
        response += f"**Cobertura**: {EMPRESA['cobertura']}\n\n"
        response += "Algunos de nuestros clientes destacados incluyen:\n"
        for cliente in EMPRESA['clientes_destacados'][:3]:
            response += f"• {cliente}\n"
        
        response += f"\nA lo largo de estos años, hemos construido una reputación sólida basada en la calidad, seguridad y servicio al cliente."
    
    # Caso por defecto, mejorado con sugerencias
    else:
        # Usar las categorías de la terminología como sugerencias
        suggested_topics = list(TERMINOLOGIA.keys())
        random.shuffle(suggested_topics)  # Mezclar para no mostrar siempre los mismos
        suggested_topics = suggested_topics[:3]  # Limitar a 3 sugerencias
        
        # Convertir términos técnicos a términos más amigables
        friendly_topics = {
            "andamios": "andamios y torres",
            "formaletas": "formaletas y encofrados",
            "columnas": "formaletas para columnas",
            "muros": "formaletas para muros",
            "losas": "sistemas para losas",
            "precio": "precios y promociones",
            "alquiler": "proceso de alquiler",
            "entrega": "logística y entregas",
            "seguridad": "normas de seguridad"
        }
        
        readable_topics = [friendly_topics.get(topic, topic) for topic in suggested_topics]
        suggestion_text = ", ".join(readable_topics[:-1]) + " o " + readable_topics[-1] if len(readable_topics) > 1 else readable_topics[0]
        
        # Comprobar si hay alguna coincidencia parcial en la pregunta
        keywords = []
        for category, terms in TERMINOLOGIA.items():
            for term in terms:
                if term in query_lower and friendly_topics.get(category) not in keywords:
                    keywords.append(friendly_topics.get(category, category))
        
        if keywords:
            response = f"No tengo información específica sobre tu consulta, pero parece que estás interesado en {', '.join(keywords)}. ¿Puedes ser más específico sobre lo que necesitas saber? Puedo ayudarte con información detallada sobre esos temas."
        else:
            response = f"No tengo información específica sobre esa consulta. Puedo ayudarte con información sobre nuestros productos, servicios y procesos. ¿Te interesaría conocer más sobre {suggestion_text}? O, si prefieres, puedo ponerte en contacto con un asesor."
            
            # Agregar sugerencias de preguntas frecuentes
            response += "\n\nAlgunas preguntas frecuentes que puedo responder:\n"
            sample_faqs = random.sample(PREGUNTAS_FRECUENTES, min(3, len(PREGUNTAS_FRECUENTES)))
            for faq in sample_faqs:
                response += f"• {faq['pregunta']}\n"
    
    # Dar un toque personal si es usuario recurrente
    if context['total_queries'] > 5:
        random_personalized_closings = [
            f"¡Gracias por tu confianza en {EMPRESA['nombre']}!",
            "Estamos siempre disponibles para asistirte.",
            "Valoramos tu preferencia por nuestros servicios.",
            "No dudes en contactarnos para cualquier otra consulta."
        ]
        response += f"\n\n{random.choice(random_personalized_closings)}"
    
    # Guardar en caché para futuras consultas
    response_cache[query_lower] = response
    response_cache_with_expiry[cache_key] = (current_time, response)
    
    return response

def generate_user_id(request):
    """Genera un ID de usuario basado en la dirección IP y el agente de usuario"""
    ip = request.META.get('REMOTE_ADDR', 'unknown')
    agent = request.META.get('HTTP_USER_AGENT', 'unknown')
    session_key = request.session.session_key or 'no_session'
    
    unique_string = f"{ip}_{agent}_{session_key}"
    return hashlib.md5(unique_string.encode()).hexdigest()

@csrf_exempt
def chat_api(request):
    """Vista que maneja las solicitudes del chatbot"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            # Generar un ID de usuario único para seguimiento de conversaciones
            user_id = generate_user_id(request)
            
            # Obtener respuesta del "modelo de IA"
            ai_response = get_ai_response(user_message, user_id)
            
            # Añadir un pequeño retraso aleatorio para simular procesamiento
            # Evita que las respuestas parezcan demasiado instantáneas/artificiales
            time.sleep(random.uniform(0.2, 0.5))
            
            # Estructurar respuesta con metadatos adicionales
            return JsonResponse({
                'response': ai_response,
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'suggestion_available': True if len(ai_response) > 50 else False  # Indica si hay sugerencias disponibles
            })
        except Exception as e:
            return JsonResponse({
                'response': 'Lo siento, hubo un error al procesar tu mensaje.',
                'status': 'error',
                'error': str(e)
            })
    
    return JsonResponse({
        'response': 'Método no permitido',
        'status': 'error'
    }, status=405)

def chat_view(request):
    """Vista para renderizar la página de chat (opcional)"""
    return render(request, 'chatbot/chat.html')