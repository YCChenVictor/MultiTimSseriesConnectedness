from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
from MultiTimeSeries_Connectedness.functions import f_volatility
from MultiTimeSeries_Connectedness.functions import f_coef
from MultiTimeSeries_Connectedness.functions import f_connectedness
import pickle

# find the path of save_file
dir_path = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = dir_path + '/save_file'

# the allowed file format
ALLOWED_EXTENSIONS = set(['csv'])


# function to determine whether to allow the file
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# begin app
app = Flask(__name__)


# setup the upload file path
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Index
@app.route('/')
def index():
    return render_template("home.html")


# upload
@app.route('/upload')
def upload_file():
    return render_template('upload.html')


# uploader when submit
@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    if request.method == 'POST':

        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        # if user does not select file, browser also submit an empty part
        # without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # save the file into store_files
        if file and allowed_file(file.filename):
            # sercure_filename make sure the file input by user is harmless.
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('upload_file'))


# read the files uploaded and calculate train
@app.route('/train', methods=['GET'])
def train():
    """
    In the future, I need to adjust the variables below
    """
    # add variables for simplicity test
    names = ["US", "UK", "Singapore", "HK", "Taiwan", "Japan", "china"]
    csv_files = ["^GSPC.csv", "^FTSE.csv", "^STI.csv", "^HSI.csv", "^TWII.csv",
                 "^N225.csv", "000001.SS.csv"]
    path = UPLOAD_FOLDER
    start_dt = "1998-09-01"
    end_dt = "2018-01-01"

    # start calculation
    Volatility = f_volatility.volatility(names, csv_files, path, start_dt,
                                         end_dt)
    Volatility.price_data_to_volatility()
    Volatility.periods_of_volatility()
    Volatility_dataframe = Volatility.dataframe

    # calculate estimated coefficients
    coef = f_coef.Coef(Volatility_dataframe, 20)
    coef.f_ols_coef()

    # save model
    with open('save_model/model.pickle', 'wb') as f:
        pickle.dump(coef, f)

    # accuracy
    accuracy = coef.accuracy

    return render_template("train.html", accuracy=accuracy)


# make plot (prediction)
@app.route('/plot', methods=['GET'])
def plot():
    """
    Should add a request method to specify the forecast period; in this case,
    the forecast period is 5.
    """
    # read saved model
    with open('save_model/model.pickle', 'rb') as f:
        coef = pickle.load(f)

    # obtain coef
    ols_coef = coef.OLS_coef

    # calculate estimated sigma given coef we want
    ols_sigma = coef.OLS_sigma

    # calculate connectedness
    conn = f_connectedness.Connectedness(ols_coef, ols_sigma)
    conn.f_full_connectedness(5)
    table = conn.full_connectedness

    # plot connectedness
    plot = 

    return render_template("plot.html", table=table, plot=plot)


if __name__ == '__main__':
    app.run(debug=True)
