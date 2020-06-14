from flask import Flask, render_template, request, Response, json
from plot_web import graph, plotAndCache

app = Flask(__name__, template_folder=".")

@app.route('/')
def default():
    return render_template('template_main.html')

@app.route('/plot')
def generatePlotData():
    cacheKey = plotAndCache(int(request.args.get('length_timeseries')),
                            int(request.args.get('no_populations')),
                            int(request.args.get('starting_number')),
                            float(request.args.get('larval_food')),
                            float(request.args.get('adult_food')),
                            float(request.args.get('hatchability')),
                            float(request.args.get('Mc')),
                            float(request.args.get('sex_ratio')),
                            int(request.args.get('x5')),
                            float(request.args.get('SenDen')),
                            float(request.args.get('SenSize')))
    return Response(cacheKey)

@app.route('/plotImage')
def plotImage():
    fig = graph(request.args.get('cacheKey'), "image")
    return Response(fig.getvalue(), mimetype='image/png')

@app.route("/timeseries", methods=['GET'])
def download_file():
    data = graph(request.args.get('cacheKey'), "excel")
    return Response(data.getvalue(), mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route("/datatable", methods=['GET'])
def show_table():
    html = graph(request.args.get('cacheKey'), "html")
    return render_template('template_data.html', datatable=html)

if __name__ == '__main__':
    app.run(debug=False)
