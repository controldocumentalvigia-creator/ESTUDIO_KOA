# Auditoría matemática — KOA Analytics V4.1

## Regla oficial de puntualidad

La desviación se calcula como:

`hora real de salida - hora programada`

### Jornada de la mañana

- Anticipada: desviación menor que 0 minutos.
- Puntual: desviación exactamente igual a 0 minutos.
- Retrasada: desviación mayor que 0 minutos.

La mañana no tiene tiempo de espera autorizado.

### Jornada de la tarde

- Anticipada: desviación menor que 0 minutos.
- Puntual: desviación entre 0 y 5 minutos, incluyendo ambos límites.
- Retrasada: desviación superior a 5 minutos.

Los cinco minutos corresponden a la espera autorizada para los usuarios. El retraso comienza en el minuto 6.

## Puntualidad general

La puntualidad general es ponderada y se calcula así:

`(puntuales de la mañana + puntuales de la tarde) / registros válidos de ambas jornadas`

No se promedian los porcentajes de las jornadas, porque pueden tener cantidades distintas de registros.

## Exclusiones

Se excluyen de puntualidad las horas vacías, valores 00:00, fechas-hora corruptas y desviaciones absolutas superiores a 180 minutos.

Los tiempos promedio, mediana, P90 y P95 usan únicamente recorridos efectivos con usuarios y duración válida.
