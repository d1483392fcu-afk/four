from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from app.routes.auth import login_required
from app.models.user_data import CarbonRecordModel, UserModel

bp = Blueprint('report', __name__)


@bp.route('/report')
@login_required
def report_page():
    records = CarbonRecordModel.get_by_user_id(g.user['id'])
    category_data = {}
    for r in records:
        category_data[r['category']] = category_data.get(r['category'], 0) + r['carbon_amount']
    return render_template('report/index.html', category_data=category_data)


@bp.route('/target', methods=('GET', 'POST'))
@login_required
def target():
    if request.method == 'POST':
        target_value = request.form.get('target_carbon_emission')
        if target_value is None or target_value == '':
            flash('請輸入減碳目標數值', 'danger')
            return redirect(url_for('report.target'))

        try:
            target_value = float(target_value)
            if target_value < 0:
                raise ValueError
        except ValueError:
            flash('請輸入有效的數字', 'danger')
            return redirect(url_for('report.target'))

        success = UserModel.update(g.user['id'], {'target_carbon_emission': target_value})
        if success:
            flash('減碳目標更新成功！', 'success')
            return redirect(url_for('ledger.index'))
        flash('更新失敗，請稍後再試。', 'danger')
        return redirect(url_for('report.target'))

    return render_template('report/target.html', target=g.user['target_carbon_emission'] or 0)
