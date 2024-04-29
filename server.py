
from flask import Flask, render_template, redirect, url_for, request, session, flash
from forms import TeamForm, ProjectForm, NewUserForm, LoginForm
from model import Team, User, Project, db, connect_to_db
# from flask_bcrypt import generate_password_hash



app = Flask(__name__)
app.secret_key = "keep this secret"
# team_form = TeamForm() #### Becouse of the way Flask-WTF works you can't instantiate the form at a global level because when the route function is called the form was instantiated befor the FLASK app was set up. #### 

@app.route("/")
def home():
    team_form = TeamForm()
    project_form = ProjectForm()
    user_form = NewUserForm()
    login_form = LoginForm()

    user_id = session.get("user_id")
    user = User.query.get(user_id)
    teams = user.teams if user else []

    team_projects = {}
    for team in teams:
        projects = Project.query.filter_by(team_id=team.id).all()
        print(projects)
        team_projects[team] = projects
        # print(f"team: {team.team_name}")
        # for project in projects:
            # print(f" - Project: {project.project_name}, Decription: {project.description}, Completed: {project.completed}")

    project_form.update_teams(teams)

    return render_template("home.html", team_form=team_form, project_form=project_form, user_form=user_form, login_form=login_form, user=user, teams=teams, team_projects=team_projects)



@app.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginForm()

    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data
        # hashed_entered_password = generate_password_hash(password)
        # print("Entered password hashed:", hashed_entered_password)

        user = User.query.filter_by(username=username).first()
        # print("Stored hashed password:", user.password)
        
        if user and password:

            # print("Stored hashed password:", user.password)
        
            session["user_id"] = user.id
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password. Please try again.", "error")


    return render_template("home.html", login_form=login_form)


@app.route("/add-team", methods=["POST"])
def add_team():
    team_form = TeamForm()

    if team_form.validate_on_submit():
        team_name = team_form.team_name.data
        user_id = session.get("user_id")
        new_team = Team(team_name, user_id)
        db.session.add(new_team)
        db.session.commit()
        return redirect(url_for("home"))
    else:
        return redirect(url_for("home"))

@app.route("/add-project", methods=["POST"])
def add_project():
    project_form = ProjectForm()
    user_id = session.get("user_id")

    user = User.query.get(user_id)
    teams = user.teams if user else []

    project_form.update_teams(teams)

    if project_form.validate_on_submit():
        project_name = project_form.project_name.data
        print(project_name)
        description = project_form.description.data
        completed = project_form.completed.data
        team_id = project_form.team_selection.data

        new_project = Project(project_name=project_name, description=description, completed=completed, team_id=team_id)

        db.session.add(new_project)
        db.session.commit()

        return redirect(url_for("home"))
    else:
        return redirect(url_for("home"))

    
@app.route("/teams")
def teams():
    # user = User.query.get(session.user_id)
    # return render_template("home.html", )
    pass

@app.route("/projects")
def projects():
    pass
    
@app.route("/create_user", methods=["POST"])
def create_user():
    user_form = NewUserForm()

    if user_form.validate_on_submit():
        username = user_form.username.data
        password = user_form.password.data

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash ("Username already exists. Please choose a different username.")
            return redirect(url_for("home"))

        # hashed_password = generate_password_hash(password)
        # print(f"Hashed password is: {hashed_password}")
        new_user = User(username=username, password= password)

        db.session.add(new_user)
        db.session.commit()

        new_user = new_user.id

        flash( "User created successfully!", "success")
        return redirect(url_for("home"))
    else:
        return redirect(url_for("home"))
    
@app.route("/delete-project/<int:project_id>", methods=["POST"])
def delete_project(project_id):
    project = Project.query.get(project_id)
    if project:
        db.session.delete(project)
        db.session.commit()
        flash("Project deleted successfully!", "success")
    else:
        flash("Project not found.", "error")
    return redirect(url_for("home"))

@app.route("/delete-team/<int:team_id>", methods=["POST"])
def delete_team(team_id):
    team = Team.query.get(team_id)
    if team:
        # Delete all associated projects
        Project.query.filter_by(team_id=team.id).delete()
        db.session.delete(team)
        db.session.commit()
        flash("Team and associated projects deleted successfully!", "success")
    else:
        flash("Team not found.", "error")
    return redirect(url_for("home"))




if __name__ == "__main__":
    connect_to_db(app)
    app.run(debug = True)