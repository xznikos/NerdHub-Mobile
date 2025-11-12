# perfil.py
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, BooleanProperty
from kivy.app import App
from database import Database
import re
from kivy.clock import Clock
from datetime import datetime, timedelta
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget

class PerfilScreen(Screen):
    username = StringProperty("")
    full_name = StringProperty("")
    email = StringProperty("")
    phone = StringProperty("")
    birth_date = StringProperty("")
    password = StringProperty("")
    show_password = BooleanProperty(False)
    new_password = StringProperty("")
    confirm_password = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
        hoje = datetime.now()
        self.current_month = hoje.month
        self.current_year = hoje.year
        self.date_popup = None
    
    def on_pre_enter(self):
        """Verifica se o usuário está logado antes de entrar na tela"""
        app = App.get_running_app()
        if not app.usuario_logado:
            print("❌ Acesso negado à tela de perfil - usuário não logado")
            app.mostrar_popup("Faça o login para acessar seu perfil!")
            self.manager.current = 'login'
            return
        
        # Se estiver logado, carrega os dados
        self.load_user_data()
    
    def load_user_data(self):
        """Carrega os dados do usuário do banco de dados"""
        app = App.get_running_app()
        if app.usuario_logado:
            print(f"🔄 Carregando dados do usuário ID: {app.usuario_logado['id']}")
            
            user_data = self.db.get_user_by_id(app.usuario_logado['id'])
            if user_data:
                self.username = user_data[1] if user_data[1] else ""
                self.full_name = user_data[1] if user_data[1] else ""
                self.email = user_data[2] if user_data[2] else ""
                
                phone_from_db = user_data[4] if len(user_data) > 4 and user_data[4] else ""
                self.phone = self.formatar_telefone(phone_from_db) if phone_from_db else ""
                
                birth_date_from_db = user_data[5] if len(user_data) > 5 and user_data[5] else ""
                self.birth_date = self.formatar_data_nascimento(birth_date_from_db) if birth_date_from_db else ""
                
                print(f"✅ Dados carregados:")
                print(f"   👤 Nome: {self.username}")
                print(f"   📧 Email: {self.email}")
                print(f"   📞 Telefone: {self.phone}")
                print(f"   🎂 Data Nascimento: {self.birth_date}")
            else:
                print("❌ Não foi possível carregar os dados do usuário")
    
    def formatar_telefone(self, telefone):
        """Formata o telefone para o padrão (XX) XXXXX-XXXX"""
        if not telefone:
            return ""
            
        numeros = re.sub(r'\D', '', str(telefone))
        
        if len(numeros) == 11:
            return f"({numeros[0:2]}) {numeros[2]} {numeros[3:7]}-{numeros[7:]}"
        elif len(numeros) == 10:
            return f"({numeros[0:2]}) {numeros[2:6]}-{numeros[6:]}"
        elif len(numeros) == 9:
            return f"{numeros[0]} {numeros[1:5]}-{numeros[5:]}"
        elif len(numeros) == 8:
            return f"{numeros[0:4]}-{numeros[4:]}"
        else:
            return telefone
    
    def formatar_data_nascimento(self, data):
        """Formata a data de nascimento para DD/MM/AAAA"""
        if not data:
            return ""
            
        numeros = re.sub(r'\D', '', str(data))
        
        if len(numeros) == 8:
            return f"{numeros[0:2]}/{numeros[2:4]}/{numeros[4:8]}"
        elif len(numeros) == 6:
            return f"{numeros[0:2]}/{numeros[2:4]}/{numeros[4:]}"
        elif len(numeros) == 4:
            return f"{numeros[0:2]}/{numeros[2:4]}"
        else:
            return data
    
    def on_phone_change(self, instance, value):
        """Callback para formatar o telefone enquanto digita"""
        numeros = re.sub(r'\D', '', value)
        
        if len(numeros) > 11:
            numeros = numeros[:11]
        
        telefone_formatado = self.formatar_telefone(numeros)
        
        if instance.text != telefone_formatado:
            instance.text = telefone_formatado
            self.phone = telefone_formatado
    
    def on_birth_date_change(self, instance, value):
        """Callback para formatar a data de nascimento enquanto digita"""
        numeros = re.sub(r'\D', '', value)
        
        if len(numeros) > 8:
            numeros = numeros[:8]
        
        data_formatada = self.formatar_data_nascimento(numeros)
        
        if instance.text != data_formatada:
            instance.text = data_formatada
            self.birth_date = data_formatada
    
    def show_date_picker(self):
        """Abre o seletor de data com calendário visual organizado"""
        # Cria o conteúdo do popup
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # CABEÇALHO - ANOS NA PRIMEIRA LINHA
        year_header = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=5)
        
        # Botão ano anterior
        btn_prev_year = Button(
            text='«', 
            size_hint_x=None, 
            width=50, 
            font_size='20sp',
            background_color=(0.8, 0.8, 0.8, 1),
            color=(0.1, 0.1, 0.1, 1)
        )
        
        # Display do ano (clicável)
        year_display = Button(
            text=str(self.current_year), 
            size_hint_x=1,
            font_size='20sp',
            bold=True,
            background_color=(0.9, 0.9, 0.9, 1),
            color=(1, 1, 1, 1)
        )
        
        # Botão próximo ano
        btn_next_year = Button(
            text='»', 
            size_hint_x=None, 
            width=50, 
            font_size='20sp',
            background_color=(0.8, 0.8, 0.8, 1),
            color=(0.1, 0.1, 0.1, 1)
        )
        
        year_header.add_widget(btn_prev_year)
        year_header.add_widget(year_display)
        year_header.add_widget(btn_next_year)
        content.add_widget(year_header)
        
        # CABEÇALHO - MESES NA SEGUNDA LINHA
        month_header = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=5)
        
        # Botão mês anterior
        btn_prev_month = Button(
            text='‹', 
            size_hint_x=None, 
            width=50, 
            font_size='24sp',
            background_color=(0.8, 0.8, 0.8, 1),
            color=(0.1, 0.1, 0.1, 1)
        )
        
        # Display do mês
        month_display = Label(
            text=self.get_month_string(self.current_month).upper(),
            size_hint_x=1,
            font_size='20sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        
        # Botão próximo mês
        btn_next_month = Button(
            text='›', 
            size_hint_x=None, 
            width=50, 
            font_size='24sp',
            background_color=(0.8, 0.8, 0.8, 1),
            color=(0.1, 0.1, 0.1, 1)
        )
        
        month_header.add_widget(btn_prev_month)
        month_header.add_widget(month_display)
        month_header.add_widget(btn_next_month)
        content.add_widget(month_header)
        
        # DIAS DA SEMANA
        weekdays = BoxLayout(orientation='horizontal', size_hint_y=None, height=35, spacing=1)
        dias_semana = ['DOM', 'SEG', 'TER', 'QUA', 'QUI', 'SEX', 'SÁB']
        for dia in dias_semana:
            lbl = Label(
                text=dia, 
                font_size='14sp', 
                bold=True,
                color=(0.1, 0.1, 0.1, 1)
            )
            weekdays.add_widget(lbl)
        content.add_widget(weekdays)
        
        # CALENDÁRIO
        self.calendar_grid = GridLayout(cols=7, rows=6, spacing=1, size_hint_y=1)
        content.add_widget(self.calendar_grid)
        
        # BOTÕES DE AÇÃO
        actions = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, spacing=10)
        
        btn_today = Button(
            text='HOJE', 
            size_hint_x=0.25,
            background_color=(0.2, 0.6, 0.8, 1),
            font_size='14sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        
        btn_clear = Button(
            text='LIMPAR', 
            size_hint_x=0.25,
            background_color=(0.8, 0.3, 0.3, 1),
            font_size='14sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        
        # BOTÃO CONFIRMAR
        btn_confirm = Button(
            text='CONFIRMAR', 
            size_hint_x=0.25,
            background_color=(0.07, 0.57, 0.38, 1),
            font_size='12sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        
        btn_cancel = Button(
            text='CANCELAR', 
            size_hint_x=0.25,
            background_color=(0.6, 0.6, 0.6, 1),
            font_size='14sp',
            color=(1, 1, 1, 1)
        )
        
        actions.add_widget(btn_today)
        actions.add_widget(btn_clear)
        actions.add_widget(btn_confirm)
        actions.add_widget(btn_cancel)
        content.add_widget(actions)
        
        # FUNÇÕES
        def update_calendar():
            self.calendar_grid.clear_widgets()
            self.populate_calendar(self.calendar_grid, self.current_month, self.current_year)
            month_display.text = self.get_month_string(self.current_month).upper()
            year_display.text = str(self.current_year)
        
        def prev_year(instance):
            self.current_year -= 1
            update_calendar()
        
        def next_year(instance):
            self.current_year += 1
            update_calendar()
        
        def prev_month(instance):
            self.current_month -= 1
            if self.current_month < 1:
                self.current_month = 12
                self.current_year -= 1
            update_calendar()
        
        def next_month(instance):
            self.current_month += 1
            if self.current_month > 12:
                self.current_month = 1
                self.current_year += 1
            update_calendar()
        
        def show_year_selector(instance):
            self.show_year_selection_popup()
        
        def set_today(instance):
            hoje = datetime.now()
            self.current_year = hoje.year
            self.current_month = hoje.month
            self.select_date_from_calendar(hoje.day, hoje.month, hoje.year)
        
        def clear_date(instance):
            self.birth_date = ""
            if hasattr(self, 'birth_date_input'):
                self.birth_date_input.text = ""
            if self.date_popup:
                self.date_popup.dismiss()
        
        def confirm_date(instance):
            # Se já tem uma data selecionada, fecha o popup
            if self.birth_date:
                if self.date_popup:
                    self.date_popup.dismiss()
            else:
                # Se não tem data selecionada, mostra mensagem
                app = App.get_running_app()
                app.mostrar_popup("Selecione uma data primeiro!")
        
        def cancel_popup(instance):
            if self.date_popup:
                self.date_popup.dismiss()
        
        # BIND DOS BOTÕES
        btn_prev_year.bind(on_release=prev_year)
        btn_next_year.bind(on_release=next_year)
        btn_prev_month.bind(on_release=prev_month)
        btn_next_month.bind(on_release=next_month)
        year_display.bind(on_release=show_year_selector)
        btn_today.bind(on_release=set_today)
        btn_clear.bind(on_release=clear_date)
        btn_confirm.bind(on_release=confirm_date)
        btn_cancel.bind(on_release=cancel_popup)
        
        # PREENCHE CALENDÁRIO
        update_calendar()
        
        # CRIA POPUP
        self.date_popup = Popup(
            title='Selecione a Data de Nascimento',
            content=content,
            size_hint=(0.9, 0.85),
            auto_dismiss=False,
            separator_height=0,
            title_color=(0.1, 0.1, 0.1, 1)
        )
        self.date_popup.open()
    
    def show_year_selection_popup(self):
        """Mostra popup para seleção rápida de ano"""
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        title = Label(
            text='Selecione o Ano', 
            size_hint_y=None, 
            height=50, 
            font_size='20sp', 
            bold=True,
            color=(0.1, 0.1, 0.1, 1)
        )
        content.add_widget(title)
        
        # Grid de anos
        years_grid = GridLayout(cols=4, spacing=8, size_hint_y=1)
        
        current_year = datetime.now().year
        start_year = current_year - 50
        end_year = current_year + 10
        
        for year in range(start_year, end_year + 1):
            is_current = (year == self.current_year)
            is_present = (year == current_year)
            
            btn = Button(
                text=str(year),
                font_size='14sp' if year >= current_year - 10 else '12sp',
                background_color=(
                    (0.07, 0.57, 0.38, 1) if is_current else
                    (0.2, 0.6, 0.8, 1) if is_present else
                    (0.9, 0.9, 0.9, 1)
                ),
                color=(
                    (1, 1, 1, 1) if is_current or is_present else 
                    (0.1, 0.1, 0.1, 1)
                )
            )
            
            def select_year(instance, y=year):
                self.current_year = y
                if self.date_popup:
                    self.date_popup.dismiss()
                Clock.schedule_once(lambda dt: self.show_date_picker(), 0.2)
            
            btn.bind(on_release=select_year)
            years_grid.add_widget(btn)
        
        content.add_widget(years_grid)
        
        btn_cancel = Button(
            text='Voltar', 
            size_hint_y=None, 
            height=50,
            background_color=(0.6, 0.6, 0.6, 1),
            font_size='16sp',
            color=(1, 1, 1, 1)
        )
        btn_cancel.bind(on_release=lambda x: year_popup.dismiss())
        content.add_widget(btn_cancel)
        
        year_popup = Popup(
            title='',
            content=content,
            size_hint=(0.8, 0.8),
            auto_dismiss=True,
            title_color=(0.1, 0.1, 0.1, 1)
        )
        year_popup.open()
    
    def get_month_string(self, month):
        """Retorna string do mês"""
        meses = [
            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]
        return meses[month-1]
    
    def populate_calendar(self, grid, month, year):
        """Preenche o grid do calendário com os dias"""
        first_day = datetime(year, month, 1)
        
        # Dias no mês
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)
        days_in_month = (next_month - first_day).days
        
        # Dia da semana do primeiro dia
        start_day = first_day.weekday() + 1
        if start_day == 7:
            start_day = 0
        
        # Dias vazios do mês anterior
        for i in range(start_day):
            btn = Button(
                text="", 
                background_color=(0.97, 0.97, 0.97, 0.3),
                color=(0.1, 0.1, 0.1, 1)
            )
            grid.add_widget(btn)
        
        # Dias do mês atual
        hoje = datetime.now()
        data_atual = None
        
        if self.birth_date:
            try:
                parts = self.birth_date.split('/')
                if len(parts) == 3:
                    data_atual = datetime(int(parts[2]), int(parts[1]), int(parts[0]))
            except:
                pass
        
        for day in range(1, days_in_month + 1):
            date_obj = datetime(year, month, day)
            is_today = (date_obj.date() == hoje.date())
            is_selected = (data_atual and date_obj.date() == data_atual.date())
            is_weekend = date_obj.weekday() in [5, 6]
            
            # CORREÇÃO: bold deve ser True ou False, nunca None
            btn_bold = is_today or is_selected
            
            btn = Button(
                text=str(day),
                font_size='16sp',
                background_color=(
                    (0.07, 0.57, 0.38, 1) if is_selected else
                    (0.9, 0.9, 0.9, 1) if is_today else
                    (0.97, 0.97, 0.97, 1) if is_weekend else
                    (1, 1, 1, 1)
                ),
                color=(
                    (1, 1, 1, 1) if is_selected else
                    (0.1, 0.1, 0.1, 1) if not is_weekend else
                    (0.5, 0.5, 0.5, 1)
                ),
                background_normal='',
                bold=btn_bold  # Agora sempre True ou False
            )
            
            btn.bind(on_release=lambda instance, d=day: self.select_date_from_calendar(d, month, year))
            grid.add_widget(btn)
        
        # Preenche os dias restantes
        total_cells = 42
        remaining_cells = total_cells - (start_day + days_in_month)
        for i in range(remaining_cells):
            btn = Button(
                text="", 
                background_color=(0.97, 0.97, 0.97, 0.3),
                color=(0.1, 0.1, 0.1, 1)
            )
            grid.add_widget(btn)
    
    def select_date_from_calendar(self, day, month, year):
        """Seleciona a data do calendário"""
        data_selecionada = f"{day:02d}/{month:02d}/{year}"
        self.birth_date = data_selecionada
        if hasattr(self, 'birth_date_input'):
            self.birth_date_input.text = data_selecionada
        
        # Agora NÃO fecha automaticamente - usuário precisa clicar em CONFIRMAR
    
    def preparar_telefone_para_banco(self, telefone_formatado):
        """Remove a formatação do telefone antes de salvar no banco"""
        if telefone_formatado:
            return re.sub(r'\D', '', telefone_formatado)
        return None
    
    def preparar_data_para_banco(self, data_formatada):
        """Remove a formatação da data antes de salvar no banco"""
        if data_formatada:
            return re.sub(r'\D', '', data_formatada)
        return None
    
    def debug_dados(self):
        """Função de debug para verificar os dados atuais"""
        print("=== DEBUG PERFIL ===")
        print(f"Nome: {self.full_name}")
        print(f"Email: {self.email}")
        print(f"Telefone: {self.phone}")
        print(f"Telefone (banco): {self.preparar_telefone_para_banco(self.phone)}")
        print(f"Data Nascimento: {self.birth_date}")
        print(f"Data Nascimento (banco): {self.preparar_data_para_banco(self.birth_date)}")
        print(f"Nova Senha: {self.new_password}")
        print("====================")
    
    def change_profile_picture(self):
        """Abre seletor de arquivos para trocar foto de perfil"""
        app = App.get_running_app()
        if not app.usuario_logado:
            app.mostrar_popup("Faça o login para usar esta funcionalidade!")
            return
            
        app.mostrar_popup("Funcionalidade em desenvolvimento!")
    
    def toggle_show_password(self):
        """Alterna entre mostrar e esconder a senha"""
        self.show_password = not self.show_password
    
    def update_personal_info(self):
        """Atualiza informações pessoais do usuário"""
        app = App.get_running_app()
        if not app.usuario_logado:
            app.mostrar_popup("Faça o login para atualizar suas informações!")
            return
        
        # DEBUG: Mostra os dados antes de salvar
        self.debug_dados()
            
        if app.usuario_logado:
            print(f"🔄 Salvando informações do usuário ID: {app.usuario_logado['id']}")
            
            # Prepara os dados para o banco (remove formatação)
            telefone_banco = self.preparar_telefone_para_banco(self.phone)
            data_banco = self.preparar_data_para_banco(self.birth_date)
            
            success = self.db.update_user_profile(
                app.usuario_logado['id'],
                nome=self.full_name,
                email=self.email,
                telefone=telefone_banco if telefone_banco else None,
                data_nascimento=data_banco if data_banco else None
            )
            
            if success:
                app.mostrar_popup("Informações atualizadas com sucesso!")
                # Atualiza o nome de usuário também
                app.usuario_logado['nome'] = self.full_name
                print("✅ Informações pessoais salvas no banco de dados!")
                
                # Recarrega os dados para confirmar
                self.load_user_data()
            else:
                app.mostrar_popup("Erro ao atualizar informações. Tente novamente.")
                print("❌ Falha ao salvar informações no banco")
    
    def change_password(self):
        """Altera a senha do usuário"""
        app = App.get_running_app()
        if not app.usuario_logado:
            app.mostrar_popup("Faça o login para alterar sua senha!")
            return
        
        if not self.new_password or not self.confirm_password:
            app.mostrar_popup("Preencha ambos os campos de senha!")
            return
        
        if self.new_password != self.confirm_password:
            app.mostrar_popup("As senhas não coincidem!")
            return
        
        if len(self.new_password) < 4:
            app.mostrar_popup("A senha deve ter pelo menos 4 caracteres!")
            return
        
        if app.usuario_logado:
            print(f"🔄 Alterando senha do usuário ID: {app.usuario_logado['id']}")
            
            success = self.db.update_password(app.usuario_logado['id'], self.new_password)
            if success:
                app.mostrar_popup("Senha alterada com sucesso!")
                self.new_password = ""
                self.confirm_password = ""
                print("✅ Senha alterada com sucesso no banco de dados!")
            else:
                app.mostrar_popup("Erro ao alterar senha!")
                print("❌ Falha ao alterar senha no banco")
    
    def switch_account(self):
        """Volta para a tela de login para trocar de conta"""
        app = App.get_running_app()
        app.usuario_logado = None
        self.manager.current = 'login'
        print("🔁 Trocar conta - redirecionando para login")
    
    def voltar_para_home(self):
        """Volta para a tela home"""
        self.manager.current = 'home'