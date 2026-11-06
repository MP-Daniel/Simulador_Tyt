"""
Servicio de Consultas, Agregaciones y Filtros Jerárquicos con Django ORM.
Cumple con las 7 consultas obligatorias y cálculo de indicadores KPI.
"""
from django.db.models import Avg, Min, Max, Count, Q, F, FloatField, ExpressionWrapper
from evaluaciones.models import Intento, RespuestaIntento, PeriodoAcademico, Curso, Matricula
from banco_preguntas.models import Categoria, Pregunta
from authentication.models import Usuario


class QueryService:

    @staticmethod
    def obtener_filtros_cascada(anio=None, periodo_id=None, curso_id=None):
        """
        Retorna las opciones de filtros jerárquicos según la selección actual:
        AÑO -> PERÍODO -> CURSO -> EJE TEMÁTICO -> ESTUDIANTE.
        Garantiza que los filtros dependientes no ofrezcan valores incompatibles.
        """
        # 1. Años disponibles
        anios = list(PeriodoAcademico.objects.values_list('anio', flat=True).distinct().order_by('-anio'))
        if not anios:
            # Fallback en caso de que aún no haya períodos creados
            anios = [2026, 2025]

        # 2. Períodos académicos
        periodos_qs = PeriodoAcademico.objects.filter(activo=True)
        if anio:
            periodos_qs = periodos_qs.filter(anio=anio)
        periodos_list = [
            {'id': p.id, 'nombre': p.nombre, 'anio': p.anio}
            for p in periodos_qs.order_by('-anio', 'nombre')
        ]

        # 3. Cursos / Grupos
        cursos_qs = Curso.objects.filter(activo=True).select_related('periodo')
        if periodo_id:
            cursos_qs = cursos_qs.filter(periodo_id=periodo_id)
        elif anio:
            cursos_qs = cursos_qs.filter(periodo__anio=anio)
        cursos_list = [
            {'id': c.id, 'nombre': c.nombre, 'codigo': c.codigo, 'periodo_nombre': c.periodo.nombre, 'anio': c.periodo.anio}
            for c in cursos_qs.order_by('nombre')
        ]

        # 4. Ejes temáticos (Categorías reales del banco de preguntas)
        ejes = [
            {'id': cat.id, 'nombre': cat.nombre}
            for cat in Categoria.objects.filter(activo=True).order_by('nombre')
        ]

        # 5. Estudiantes del grupo filtrado
        estudiantes_qs = Usuario.objects.filter(rol__nombre='Estudiante', is_active=True)
        if curso_id:
            estudiantes_qs = estudiantes_qs.filter(matriculas__curso_id=curso_id)
        elif periodo_id:
            estudiantes_qs = estudiantes_qs.filter(matriculas__curso__periodo_id=periodo_id)
        elif anio:
            estudiantes_qs = estudiantes_qs.filter(matriculas__curso__periodo__anio=anio)

        estudiantes_list = [
            {
                'id': e.id,
                'nombre_completo': e.get_full_name() or e.username,
                'codigo': e.codigo_estudiantil or e.username,
                'username': e.username
            }
            for e in estudiantes_qs.distinct().order_by('last_name', 'first_name', 'username')
        ]

        return {
            'anios': anios,
            'periodos': periodos_list,
            'cursos': cursos_list,
            'ejes': ejes,
            'estudiantes': estudiantes_list
        }

    @staticmethod
    def filtrar_intentos(filtros=None):
        """
        Construye el QuerySet base de intentos finalizados aplicando los filtros acumulativos.
        """
        filtros = filtros or {}
        qs = Intento.objects.filter(estado_intento='finalizado').select_related(
            'cuestionario', 'estudiante', 'curso', 'curso__periodo'
        )

        anio = filtros.get('anio')
        periodo_id = filtros.get('periodo_id')
        curso_id = filtros.get('curso_id')
        categoria_id = filtros.get('categoria_id')
        estudiante_id = filtros.get('estudiante_id')
        busqueda = filtros.get('busqueda')
        orden = filtros.get('orden', '-fecha_inicio')

        if anio:
            qs = qs.filter(Q(curso__periodo__anio=anio) | Q(cuestionario__fecha_apertura__year=anio))

        if periodo_id:
            qs = qs.filter(curso__periodo_id=periodo_id)

        if curso_id:
            qs = qs.filter(curso_id=curso_id)

        if estudiante_id:
            qs = qs.filter(estudiante_id=estudiante_id)

        if categoria_id:
            # Filtra intentos con respuestas en el eje temático seleccionado
            qs = qs.filter(respuestas__pregunta__categoria_id=categoria_id).distinct()

        if busqueda:
            term = str(busqueda).strip()
            qs = qs.filter(
                Q(estudiante__first_name__icontains=term) |
                Q(estudiante__last_name__icontains=term) |
                Q(estudiante__codigo_estudiantil__icontains=term) |
                Q(estudiante__username__icontains=term)
            )

        # Ordenamiento
        orden_map = {
            'nombre_asc': ['estudiante__last_name', 'estudiante__first_name'],
            'nombre_desc': ['-estudiante__last_name', '-estudiante__first_name'],
            'fecha_asc': ['fecha_inicio'],
            'fecha_desc': ['-fecha_inicio'],
            'nota_asc': ['calificacion'],
            'nota_desc': ['-calificacion'],
        }
        if orden in orden_map:
            qs = qs.order_by(*orden_map[orden])
        else:
            qs = qs.order_by('-fecha_inicio')

        return qs

    @staticmethod
    def calcular_indicadores(qs):
        """
        Calcula las 6 métricas estadísticas clave sobre el conjunto de intentos filtrado.
        """
        total_intentos = qs.count()
        if total_intentos == 0:
            return {
                'estudiantes_evaluados': 0,
                'intentos_finalizados': 0,
                'calificacion_promedio': 0.00,
                'calificacion_minima': 0.00,
                'calificacion_maxima': 0.00,
                'aprobados': 0,
                'reprobados': 0,
                'porcentaje_aprobacion': 0.00,
                'umbral_aprobacion': 3.00
            }

        estudiantes_evaluados = qs.values('estudiante').distinct().count()
        agregados = qs.aggregate(
            prom=Avg('calificacion'),
            mini=Min('calificacion'),
            maxi=Max('calificacion'),
            aprobados=Count('id', filter=Q(resultado='aprobado')),
            reprobados=Count('id', filter=Q(resultado='reprobado'))
        )

        aprobados = agregados['aprobados'] or 0
        porcentaje_aprobacion = round((aprobados / total_intentos) * 100.0, 2)

        return {
            'estudiantes_evaluados': estudiantes_evaluados,
            'intentos_finalizados': total_intentos,
            'calificacion_promedio': round(float(agregados['prom'] or 0.0), 2),
            'calificacion_minima': round(float(agregados['mini'] or 0.0), 2),
            'calificacion_maxima': round(float(agregados['maxi'] or 0.0), 2),
            'aprobados': aprobados,
            'reprobados': agregados['reprobados'] or 0,
            'porcentaje_aprobacion': porcentaje_aprobacion,
            'umbral_aprobacion': 3.00
        }

    # =========================================================================
    # LAS 7 CONSULTAS OBLIGATORIAS (Sección 6)
    # =========================================================================

    @classmethod
    def consulta_consolidado_general(cls, filtros=None):
        """
        Consulta 1: Consolidado general de evaluaciones.
        Retorna la lista detallada de intentos finalizados con datos de estudiante y curso.
        """
        qs = cls.filtrar_intentos(filtros)
        registros = []
        for i in qs:
            curso_nombre = i.curso.nombre if i.curso else (i.estudiante.matriculas.first().curso.nombre if i.estudiante.matriculas.exists() else 'Sin curso')
            periodo_nombre = i.curso.periodo.nombre if i.curso else (i.estudiante.matriculas.first().curso.periodo.nombre if i.estudiante.matriculas.exists() else 'N/A')
            anio_val = i.curso.periodo.anio if i.curso else (i.cuestionario.fecha_apertura.year if i.cuestionario.fecha_apertura else 2026)

            registros.append({
                'intento_id': i.id,
                'anio': anio_val,
                'periodo': periodo_nombre,
                'curso': curso_nombre,
                'estudiante_id': i.estudiante_id,
                'estudiante_nombre': i.estudiante.get_full_name() or i.estudiante.username,
                'estudiante_codigo': i.estudiante.codigo_estudiantil or i.estudiante.username,
                'simulacro': i.cuestionario.nombre,
                'cuestionario_id': i.cuestionario_id,
                'fecha': i.fecha_inicio.strftime('%Y-%m-%d %H:%M') if i.fecha_inicio else '',
                'calificacion': float(i.calificacion),
                'estado': 'Aprobado' if i.resultado == 'aprobado' else 'Reprobado',
                'aciertos': i.aciertos,
                'errores': i.errores,
                'omitidas': i.omitidas
            })
        return registros

    @classmethod
    def consulta_por_periodo(cls, filtros=None):
        """
        Consulta 2: Resultados por año y período académico.
        Compara cantidad de evaluaciones, promedio y porcentaje de aprobación.
        """
        qs = cls.filtrar_intentos(filtros)
        data = qs.values(
            'curso__periodo__anio', 'curso__periodo__nombre'
        ).annotate(
            total_evaluaciones=Count('id'),
            promedio=Avg('calificacion'),
            nota_minima=Min('calificacion'),
            nota_maxima=Max('calificacion'),
            aprobados=Count('id', filter=Q(resultado='aprobado')),
            reprobados=Count('id', filter=Q(resultado='reprobado'))
        ).order_by('-curso__periodo__anio', 'curso__periodo__nombre')

        resultados = []
        for row in data:
            anio = row['curso__periodo__anio'] or 2026
            periodo = row['curso__periodo__nombre'] or 'Consolidado General'
            tot = row['total_evaluaciones']
            apr = row['aprobados']
            pct = round((apr / tot * 100.0), 2) if tot > 0 else 0.0

            resultados.append({
                'anio': anio,
                'periodo': periodo,
                'total_evaluaciones': tot,
                'promedio': round(float(row['promedio'] or 0.0), 2),
                'nota_minima': round(float(row['nota_minima'] or 0.0), 2),
                'nota_maxima': round(float(row['nota_maxima'] or 0.0), 2),
                'aprobados': apr,
                'reprobados': row['reprobados'],
                'porcentaje_aprobacion': pct
            })
        return resultados

    @classmethod
    def consulta_por_curso(cls, filtros=None):
        """
        Consulta 3: Resultados por curso o grupo.
        Estudiantes evaluados, promedio, nota mínima y máxima por curso/grupo.
        """
        qs = cls.filtrar_intentos(filtros)
        data = qs.values(
            'curso__id', 'curso__nombre', 'curso__periodo__nombre', 'curso__periodo__anio'
        ).annotate(
            estudiantes_evaluados=Count('estudiante', distinct=True),
            total_intentos=Count('id'),
            promedio=Avg('calificacion'),
            nota_minima=Min('calificacion'),
            nota_maxima=Max('calificacion'),
            aprobados=Count('id', filter=Q(resultado='aprobado'))
        ).order_by('curso__nombre')

        resultados = []
        for row in data:
            curso_nombre = row['curso__nombre'] or 'Sin Curso Asignado'
            tot = row['total_intentos']
            apr = row['aprobados']
            pct = round((apr / tot * 100.0), 2) if tot > 0 else 0.0

            resultados.append({
                'curso_id': row['curso__id'],
                'curso_nombre': curso_nombre,
                'periodo': row['curso__periodo__nombre'] or 'N/A',
                'anio': row['curso__periodo__anio'] or 2026,
                'estudiantes_evaluados': row['estudiantes_evaluados'],
                'total_intentos': tot,
                'promedio': round(float(row['promedio'] or 0.0), 2),
                'nota_minima': round(float(row['nota_minima'] or 0.0), 2),
                'nota_maxima': round(float(row['nota_maxima'] or 0.0), 2),
                'porcentaje_aprobacion': pct
            })
        return resultados

    @classmethod
    def consulta_desempeno_ejes(cls, filtros=None):
        """
        Consulta 4: Desempeño por eje temático.
        Regla: Calculado estrictamente desde respuestas efectivamente contestadas (opcion_seleccionada!=NULL).
        """
        qs_intentos = cls.filtrar_intentos(filtros)
        respuestas = RespuestaIntento.objects.filter(
            intento__in=qs_intentos,
            opcion_seleccionada__isnull=False
        )

        data = respuestas.values(
            'pregunta__categoria__id', 'pregunta__categoria__nombre'
        ).annotate(
            total_respondidas=Count('id'),
            aciertos=Count('id', filter=Q(es_acierto=True)),
            errores=Count('id', filter=Q(es_acierto=False))
        ).order_by('pregunta__categoria__nombre')

        resultados = []
        for row in data:
            tot = row['total_respondidas']
            aciertos = row['aciertos']
            pct = round((aciertos / tot * 100.0), 2) if tot > 0 else 0.0
            resultados.append({
                'categoria_id': row['pregunta__categoria__id'],
                'eje_tematico': row['pregunta__categoria__nombre'] or 'Sin categoría',
                'total_respondidas': tot,
                'aciertos': aciertos,
                'errores': row['errores'],
                'porcentaje_acierto': pct
            })
        return resultados

    @classmethod
    def consulta_calificaciones_estudiante(cls, filtros=None):
        """
        Consulta 5: Calificaciones por estudiante.
        Muestra Estudiante, curso, simulacro, fecha, nota sobre 5.0 y estado.
        """
        qs = cls.filtrar_intentos(filtros)
        resultados = []
        for i in qs:
            curso_nom = i.curso.nombre if i.curso else 'Sin curso'
            resultados.append({
                'intento_id': i.id,
                'estudiante_id': i.estudiante_id,
                'estudiante_nombre': i.estudiante.get_full_name() or i.estudiante.username,
                'estudiante_codigo': i.estudiante.codigo_estudiantil or i.estudiante.username,
                'curso': curso_nom,
                'simulacro': i.cuestionario.nombre,
                'fecha': i.fecha_inicio.strftime('%Y-%m-%d %H:%M') if i.fecha_inicio else '',
                'calificacion': float(i.calificacion),
                'estado': 'Aprobado' if i.resultado == 'aprobado' else 'Reprobado'
            })
        return resultados

    @classmethod
    def consulta_historial_individual(cls, filtros=None, estudiante_id=None):
        """
        Consulta 6: Historial individual de un estudiante.
        Intentos del estudiante en orden cronológico, fechas, resultados y evolución de notas.
        """
        f = (filtros or {}).copy()
        if estudiante_id:
            f['estudiante_id'] = estudiante_id
            f['busqueda'] = None

        qs = cls.filtrar_intentos(f).order_by('fecha_inicio')
        resultados = []
        for i in qs:
            curso_nom = i.curso.nombre if i.curso else 'N/A'
            periodo_nom = i.curso.periodo.nombre if i.curso else 'N/A'
            tot_resp = i.aciertos + i.errores

            resultados.append({
                'intento_id': i.id,
                'numero_intento': i.numero_intento,
                'estudiante_id': i.estudiante_id,
                'estudiante_nombre': i.estudiante.get_full_name() or i.estudiante.username,
                'curso': curso_nom,
                'periodo': periodo_nom,
                'simulacro': i.cuestionario.nombre,
                'fecha': i.fecha_inicio.strftime('%Y-%m-%d %H:%M') if i.fecha_inicio else '',
                'preguntas_respondidas': tot_resp,
                'aciertos': i.aciertos,
                'errores': i.errores,
                'omitidas': i.omitidas,
                'nota_final': float(i.calificacion),
                'estado': 'Aprobado' if i.resultado == 'aprobado' else 'Reprobado'
            })
        return resultados

    @classmethod
    def consulta_preguntas_dificultad(cls, filtros=None):
        """
        Consulta 7: Preguntas de mayor dificultad.
        Pregunta/identificador, eje, total respuestas, errores y % de acierto.
        Ordenado de menor porcentaje de acierto a mayor (más difíciles primero).
        """
        qs_intentos = cls.filtrar_intentos(filtros)
        respuestas = RespuestaIntento.objects.filter(
            intento__in=qs_intentos,
            opcion_seleccionada__isnull=False
        )

        data = respuestas.values(
            'pregunta__id', 'pregunta__enunciado', 'pregunta__categoria__nombre'
        ).annotate(
            total_respuestas=Count('id'),
            aciertos=Count('id', filter=Q(es_acierto=True)),
            errores=Count('id', filter=Q(es_acierto=False))
        )

        resultados = []
        for row in data:
            tot = row['total_respuestas']
            aciertos = row['aciertos']
            pct = round((aciertos / tot * 100.0), 2) if tot > 0 else 0.0

            enunciado = row['pregunta__enunciado'] or ''
            if len(enunciado) > 90:
                enunciado = enunciado[:87] + '...'

            resultados.append({
                'pregunta_id': row['pregunta__id'],
                'enunciado': enunciado,
                'eje_tematico': row['pregunta__categoria__nombre'] or 'Sin categoría',
                'total_respuestas': tot,
                'aciertos': aciertos,
                'errores': row['errores'],
                'porcentaje_acierto': pct
            })

        # Ordenar por menor porcentaje de acierto y mayor cantidad de errores
        resultados.sort(key=lambda x: (x['porcentaje_acierto'], -x['errores']))
        return resultados
