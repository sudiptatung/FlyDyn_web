from flask import Flask, render_template, request, Response, json

app = Flask(__name__, template_folder=".")


@app.route('/')
def default():
    return render_template('template_1.html')


@app.route('/plotImage')
def plotImage():
    from plot_web import graph
    global data
    global html
    (fig, data, html) = graph(int(request.args.get('length_timeseries')), int(request.args.get('no_populations')), int(request.args.get('starting_number')), float(request.args.get('larval_food')), float(request.args.get('adult_food')), float(request.args.get('hatchability')), float(request.args.get('Mc')), float(request.args.get('sex_ratio')), int(request.args.get('x5')), float(request.args.get('SenDen')), float(request.args.get('SenSize')))
    return Response(fig.getvalue(), mimetype='image/png')

@app.route("/timeseries", methods=['GET'])
def download_file():
    return Response(data.getvalue(), mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route("/datatable", methods=['GET'])
def show_table():
    return render_template('template_data.html', datatable = html)
	
if __name__ == '__main__':
    app.run(debug = True)