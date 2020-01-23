from flask import Flask, render_template, Response, request
from kafka import KafkaConsumer, KafkaProducer
from flask import jsonify
import json

app = Flask(__name__)

broker = "localhost:9092"
topic = "all-chat"

producer = KafkaProducer(bootstrap_servers=broker, value_serializer=lambda v: json.dumps(v).encode('utf-8'))

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/stream/')
def stream():
	consumer = KafkaConsumer(bootstrap_servers=broker, value_deserializer = lambda m: json.loads(m.decode('utf-8')))
	consumer.subscribe(topics=[topic])

	def eventStream():
		for message in consumer:
			yield 'data: {0}\n\n'.format(message.value)

	return Response(eventStream(), mimetype="text/event-stream")

@app.route('/send/', methods=['GET', 'POST'])
def post():
	if request.method == 'POST':
		data = request.form
		message = producer.send(topic, json.dumps(data))
		return Response({
			"success": True,
			"message": "OK"
		})
	return "Invalid request method"

if __name__ == '__main__':
	app.debug = True
	app.run()