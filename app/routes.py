from flask import redirect, session, render_template, send_from_directory, url_for, request, current_app
from app.ModelsManager import ModelsManager
from app.DbManager import DbManager


def init_routes(app):
	@app.route('/resources/<path:filename>')
	def custom_static(filename):
		return send_from_directory('../resources/', filename)

	@app.route("/", methods=["GET", "POST"])
	@app.route("/index", methods=["GET", "POST"])
	def index():
		DbManager.g_create_table()
		DbManager.load_images_to_db()

		DbManager.clear_answers()
		DbManager.delete_recolored()

		ModelsManager.mark_dtypes_in_db()

		session['answer_amount'] = 0
		session['answer_amount_recolored'] = 0
		session['recolored_amount'] = 0
		session['stage2'] = False
		session['no_daltonism'] = False

		session.modified = True

		return render_template("index.html")

	@app.route("/form")
	def form():
		if 'stage2' not in session:
			return redirect(url_for('index'))

		if not session['stage2']:
			if 'image_paths' not in session:
				session['image_paths'] = DbManager.g_get_n_random_pics(app.config["IMG_AMOUNT"])
			session['jinja_image_path'] = session['image_paths'][session['answer_amount']][1]
		else:
			wrong_ans = DbManager.g_get_with_wrong_ans([t[1] for t in session['image_paths']])

			if 'dalton_type' not in session:
				session["dalton_type"] = ModelsManager.define_type(session['image_paths'])

			if 'image_paths_recolored' not in session:
				session['image_paths_recolored'] = ModelsManager.recolor_images(wrong_ans, session["dalton_type"] ) # TODO: sometimes it returns 0 pathes when wrong answer > 0


			if len(session['image_paths_recolored']) > 0:
				session['next_recoloured_img_path'] = session['image_paths_recolored'].pop(0)
			else:
				session['no_daltonism'] = True
				return redirect("/result")

			if len(session['image_paths_recolored']) > 0:
				session['jinja_image_path'] = session['next_recoloured_img_path']
			else:
				return redirect(url_for('result'))

		jinja_img = url_for('custom_static', filename=session['jinja_image_path'])
		return render_template("form.html", jinja_image_path=jinja_img)

	@app.route("/process_answer", methods=["POST"])
	def process_answer():
		if 'stage2' not in session:
			return redirect(url_for('index'))

		if not session['stage2']:
			session['answer_amount'] += 1
			DbManager.insert_answer(session['jinja_image_path'], request.form.get('answer'))

			if session['answer_amount'] >= app.config['IMG_AMOUNT']:
				session['stage2'] = True
			return redirect("/form")

		session['answer_amount_recolored'] += 1
		DbManager.insert_answer(session['jinja_image_path'], request.form.get('answer'))
		return redirect("/form")

	@app.route("/result", methods=["GET", "POST"])
	def result():
		if 'no_daltonism' not in session:
			return redirect(url_for('index'))

		if session['no_daltonism']:
			return render_template("result.html", dalton_type=-1, percentage=0)
		else:
			if 'dalton_type' not in session:
				return redirect(url_for('index'))

			d_type, percent = ModelsManager.get_correctness_chance(session["dalton_type"])
			DbManager.clear_answers()
			DbManager.delete_recolored()

			if d_type == 0:
				d_type = "DEUTAN"
			elif d_type == 1:
				d_type = "PROTAN"
			else:
				d_type = "TRITAN"

			session.clear()  # Clear session to start new test fresh
			return render_template("result.html", dalton_type=d_type, percentage=percent)
