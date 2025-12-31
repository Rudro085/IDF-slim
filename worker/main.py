# from templates.mtb_parse import Mtb_parser
# from templates.ebl_parse import Ebl_parser
# from templates.midland_parse import Midland_parser
# from templates.sonali_parse import Sonali_parser
# from templates.ucb_parse import Ucb_parser
# from utils.pipeline import Pipeline



# if __name__ == "__main__":
#     pipeline = Pipeline()
#     pipeline.add_template(Ebl_parser())
#     pipeline.add_template(Mtb_parser())
#     pipeline.add_template(Midland_parser())
#     pipeline.add_template(Sonali_parser())
#     pipeline.add_template(Ucb_parser())



#     st = pipeline.parse('uploaded_pdfs/ebl.pdf',bank_name='EBL')
    
#     st.show()
#     # print(st.validate())
#     st.save_to_csv("ucb_test.csv")
from templates.ebl.ebl import Ebl
from templates.midland.midland import Midland
from templates.mtb.mtb import Mtb
from templates.sonali.sonali import Sonali
from templates.ucb.ucb import Ucb
from utils import category
bank = Ucb()
st = bank.run('uploaded_pdfs/UCB162.pdf',bank_name='UCB')
#st.show()
#st.save_to_csv("ebl_siam.csv")

search_result = category.search_transactions(st,'credit commerce')
print(search_result)