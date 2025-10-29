from flask import Flask, render_template
from flask_cors import CORS
from routes.simulation import simulation_bp
from routes.disruptions import disruptions_bp
from routes.recovery import recovery_bp

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(simulation_bp, url_prefix='/api')
app.register_blueprint(disruptions_bp, url_prefix='/api')
app.register_blueprint(recovery_bp, url_prefix='/api')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/map')
def map_view():
    return render_template('map.html')

@app.route('/analytics')
def analytics_view():
    return render_template('analytics.html')

if __name__ == '__main__':
    app.run(debug=True)