import time
import streamlit as st
from hydralit import HydraHeadApp
from hydralit_components import HyLoader, Loaders


class LoadingApp(HydraHeadApp):

    def __init__(self, title = 'Loader', delay=0,loader=Loaders.standard_loaders, **kwargs):
        self.__dict__.update(kwargs)
        self.title = title
        self.delay = delay
        self._loader = loader

    def run(self,app_target):

        try:

            se_loader_txt = """
            <style>
#rcorners1 {
  border-radius: 25px;
  background: grey;
  color: #00000;
  alignment: center;
  opacity: 0.95;
  padding: 20px;
  width: 1920px;
  height: 400px;
  z-index: 9998;
}
#banner {
  color: white;
  vertical-align: text-top;
  text-align: center;
  z-index: 9999;
}
</style>
<div id="rcorners1">
<h1 id="banner">Now loading Sequency Denoising</h1>
<br>
</div>
            """
            app_title = ''
            if hasattr(app_target,'title'):
                app_title = app_target.title

            if app_title == 'Sequency Denoising':
                with HyLoader(se_loader_txt, loader_name=Loaders.pacman):
                    time.sleep(int(self.delay))
                    app_target.run()

            elif app_title == 'Loader Playground':
                app_target.run()
            else:
                with HyLoader("✨Now loading {}".format(app_title), loader_name=self._loader,index=[3,0,5]):
                    time.sleep(int(self.delay))
                    app_target.run()



        except Exception as e:
            st.image("./resources/failure.png",width=100,)
            st.error('An error has occurred, someone will be punished for your inconvenience, we humbly request you try again.')
            st.error('Error details: {}'.format(e))

