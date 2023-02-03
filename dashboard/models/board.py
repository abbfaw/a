from odoo import fields, models, api


class BoardBoardInherit(models.Model):
	_name = "board.board.inherit"

	def _board_action_server(self):

		print("Dans l'actionserver", self)
		# self._set_top_customer()
		action = {
			'name': "Mon tableau de bord",
			'type': "ir.actions.act_window",
			'res_model': 'board.board',
			'view_mode': 'form',
			'usage': 'menu',
			'view_id': self.env.ref('dashboard.board_my_dash_purchase_view').id
		}

		return action