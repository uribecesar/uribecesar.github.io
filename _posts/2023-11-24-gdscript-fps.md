---
layout: post
title:  GDScript - Optimización del Control de Personaje en FPS
date: 2023-11-24 07:12:00
description: Codigo fuente para el control de personaje dinamico en Godot
tags: programacion godot gdscript gamedev
categories: General
thumbnail: assets/img/godot_0.jpg
giscus_comments: true
---

[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Godot Engine](https://img.shields.io/badge/godot-4.1%2B-blue.svg)](https://godotengine.org/)
[![Version](https://img.shields.io/badge/version-v1.0.0-orange.svg)](https://github.com/tuusuario/tuproyecto/releases/tag/v1.0.0)




Control de personaje para juegos en primera persona (FPS) desarrollado en Godot Engine. Este código proporciona una implementación optimizada para gestionar el movimiento y las interacciones del personaje.

{% include figure.html path="assets/img/godot_1.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
---

### Características Principales

- Transiciones suaves entre estados de movimiento (caminar, correr, agacharse).
- Dinámico sistema de deslizamiento para experiencias de juego emocionantes.
- Efectos visuales realistas, como el balanceo de cabeza durante acciones específicas.
- Interacción fluida del personaje con el entorno mediante detección de colisiones y rayos.
  
---

### Instrucciones de Uso

1. **Integración en Proyectos:**
   - Incorpora el código fuente en tu proyecto Godot Engine.
   - No olvides ajustar los valores de movimiento en el mapa de entradas (`input map`) según tus necesidades.
{% include figure.html path="assets/img/godot_2.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
2. **Resolución de Problemas:**
   - Al ejecutar la escena, verifica las rutas de dependencias para asegurar la correcta vinculación de recursos.
   {% include figure.html path="assets/img/godot_3.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}

---




### Descarga

Como contribución práctica a la comunidad este es el codigo y el enlace a al respositorio en [github](https://github.com/uribecesar/fps-godot-simple) 

```gdscript
extends CharacterBody3D

#PLAYER NODES
#"left", "right", "forward", "backward", "freelook","crouch","jump"
@onready var eyes = $nek/head/eyes
@onready var camera_3d = $nek/head/eyes/Camera3D
@onready var nek = $nek

@onready var head = $nek/head
@onready var standing_collision_shape = $StandingCollisionShape
@onready var crouching_collision_shape = $CrouchingCollisionShape
@onready var ray_cast_3d = $RayCast3D

#SPEED VARIRABLES

@export var walking_speed = 5.0
@export var sprinting_speed = 8.0
@export var crouching_speed = 3.0
@export var gravity = 10.0
@export var booleantest = false
@export var stringTest = "String1"
@export var integerTest = 10

var current_speed = walking_speed

#STATES
var walking = false
var sprinting = false
var crouching = false
var free_looking = false
var sliding = false

#SLIDE VARS

var slide_timer = 0.0
var slide_timer_max= 1.0
var slide_vector= Vector2.ZERO
@export var slide_speed=10.0

#HEAD bobbing vars

const head_bobbing_sprint_speed = 22.0
const head_bobbing_walking_speed = 14.0
const head_bobbing_crouching_speed =  10.0

const head_bobbing_sprint_intensity = 0.2
const head_bobbing_walking_intensity = 0.1
const head_bobbing_crouching_intensity = 0.05

var head_bobbing_vector = Vector2.ZERO
var head_bobbing_index = 0.0
var head_bobbing_current_intesity = 0.0

#MOVEMENT VARS 
#var for incrementally reach intended speed, set to 0 for snappy movement
@export var lerp_speed = 10.0

@export var jump_velocity = 4.5

var crouching_depth = -0.5 #Ctodo: fix this

var tilt_amount_freelook = 8

@export var air_lerp_speed = 3.0

#INPUT VARS
var direction = Vector3.ZERO
@export var mouse_sens = 0.1




# Get the gravity from the project settings to be synced with RigidBody nodes.


func _ready():
	Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)


func _input(event):
	#gives action to mouse movement
	if event is InputEventMouseMotion:
		if free_looking:
			nek.rotate_y(deg_to_rad(-event.relative.x * mouse_sens))
			nek.rotation.y=clamp(nek.rotation.y, deg_to_rad(-120), deg_to_rad(120))
		else:
			rotate_y(deg_to_rad(-event.relative.x * mouse_sens))
		head.rotate_x(deg_to_rad(-event.relative.y * mouse_sens))
		#restricts head rotation
		head.rotation.x=clamp(head.rotation.x, deg_to_rad(-89), deg_to_rad(89))
		

		
#HANDLE MOVEMENT	
func _physics_process(delta):
	#getting movement input
	var input_dir = Input.get_vector("left", "right", "forward", "backward")
	
	#movement states
	
	#crouching
	
	if  Input.is_action_pressed("crouch") || sliding:
		
		current_speed = lerp(current_speed, crouching_speed, delta*lerp_speed)
		head.position.y = lerp(head.position.y,crouching_depth, delta*lerp_speed)
		
		standing_collision_shape.disabled=true
		crouching_collision_shape.disabled=false
		
		#Slide Begin Logic
		
		if sprinting && input_dir != Vector2.ZERO:
			sliding=true
			slide_timer = slide_timer_max
			slide_vector = input_dir
			free_looking=true
			print("slide beging")
		
		walking = false
		sprinting = false
		crouching = true
	
	elif !ray_cast_3d.is_colliding():
		
		#STANDING
		
		standing_collision_shape.disabled = false
		crouching_collision_shape.disabled = true
		
		head.position.y = lerp(head.position.y,0.0, delta*lerp_speed)
		
		if Input.is_action_pressed("sprint"):
			#sprinting
			current_speed = lerp(current_speed, sprinting_speed, delta*lerp_speed)
			
			walking = false
			sprinting = true
			crouching = false
		else:
			#walking
			current_speed=lerp(current_speed, walking_speed , delta*lerp_speed)
			
			walking = true
			sprinting = false
			crouching = false
			
			
	#HANDLE FREE LOOKING
	if Input.is_action_pressed("freelook") || sliding:
		free_looking=true
		
		if sliding:
			camera_3d.rotation.z = lerp(camera_3d.rotation.z,-deg_to_rad(7.0),delta*lerp_speed)
		else:
			camera_3d.rotation.z = -deg_to_rad(nek.rotation.y*tilt_amount_freelook)
	else:
		free_looking=false
		nek.rotation.y = lerp(nek.rotation.y, 0.0, delta*lerp_speed)
		camera_3d.rotation.z = lerp(camera_3d.rotation.z,0.0,delta*lerp_speed)
		
	#HANDLE SLIDING
		
	if sliding:
		slide_timer -=delta
		if slide_timer <= 0:
			sliding=false
			print("SLIDE END")
			free_looking=false
			
	#HANDLE HEADBOB
	if sprinting:
		head_bobbing_current_intesity = head_bobbing_sprint_intensity
		head_bobbing_index += head_bobbing_sprint_speed*delta
	elif walking:
		head_bobbing_current_intesity = head_bobbing_walking_intensity
		head_bobbing_index += head_bobbing_walking_speed*delta
	elif crouching:
		head_bobbing_current_intesity = head_bobbing_crouching_intensity
		head_bobbing_index += head_bobbing_crouching_speed*delta
		
	if is_on_floor() && !sliding && input_dir != Vector2.ZERO:
		head_bobbing_vector.y = sin(head_bobbing_index)
		head_bobbing_vector.x = sin(head_bobbing_index/2)+0.5
		
		eyes.position.y = lerp(eyes.position.y, head_bobbing_vector.y*(head_bobbing_current_intesity/2), delta*lerp_speed) 	
		eyes.position.x = lerp(eyes.position.x, head_bobbing_vector.x*(head_bobbing_current_intesity), delta*lerp_speed)
	else:
		eyes.position.y = lerp(eyes.position.y,0.0, delta*lerp_speed) 	
		eyes.position.x = lerp(eyes.position.x,0.0, delta*lerp_speed)
		
	# Add the gravity.
	if not is_on_floor():
		velocity.y -= gravity * delta

	# Handle Jump.
	if Input.is_action_just_pressed("jump") and is_on_floor():
		velocity.y = jump_velocity
		sliding = false

	# Get the input direction and handle the movement/deceleration.
	# As good practice, you should replace UI actions with custom gameplay actions.
	if is_on_floor():
		direction = lerp(direction, (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized(), delta*lerp_speed)
	else:
		if input_dir != Vector2.ZERO:
			direction = lerp(direction, (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized(), delta*air_lerp_speed)

	if sliding:
		direction = (transform.basis * Vector3(slide_vector.x,0,slide_vector.y)).normalized()
		current_speed= (slide_timer+0.1) * slide_speed

	if direction:
		velocity.x = direction.x * current_speed
		velocity.z = direction.z * current_speed
		

	else:
		velocity.x = move_toward(velocity.x, 0, current_speed)
		velocity.z = move_toward(velocity.z, 0, current_speed)

	move_and_slide()

```


