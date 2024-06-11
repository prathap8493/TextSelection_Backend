from supertokens_python import init, InputAppInfo, SupertokensConfig
from supertokens_python.recipe import emailpassword, session
from supertokens_python.recipe.thirdparty.provider import ProviderInput, ProviderConfig, ProviderClientConfig
from supertokens_python.recipe import thirdpartyemailpassword
from supertokens_python.recipe import dashboard
from supertokens_python.recipe import emailpassword
from supertokens_python.recipe import emailverification
from supertokens_python.ingredients.emaildelivery.types import EmailDeliveryConfig, SMTPSettingsFrom, SMTPSettings
from .config_factory import ConfigFactory
from supertokens_python.recipe.emailverification.types import EmailDeliveryOverrideInput, EmailTemplateVars,VerificationEmailTemplateVars
from typing import Dict, Any
from .mailmodo_utils import MailmodoUtils
import os
from dotenv import load_dotenv
load_dotenv()
import time
import sib_api_v3_sdk
from sib_api_v3_sdk import Configuration, ApiClient, TransactionalEmailsApi, SendSmtpEmail
from sib_api_v3_sdk.rest import ApiException
from pprint import pprint
from supertokens_python.recipe import usermetadata
import requests
import json
from supertokens_python.recipe import thirdpartyemailpassword, session
from supertokens_python.recipe.thirdpartyemailpassword.interfaces import RecipeInterface, EmailPasswordSignInOkResult, EmailPasswordSignUpOkResult
from supertokens_python.recipe.thirdparty.types import RawUserInfoFromProvider
from typing import Dict, Any
from supertokens_python.recipe.usermetadata.asyncio import update_user_metadata
from chat_app.database.queries.user_meta_data_queries import UserMetaDataQueries

ConfigFactory.load_config()
smtp_settings = SMTPSettings(
    host="smtp.gmail.com",
    port=465,
    from_=SMTPSettingsFrom(
        name="Content Detector",
        email="hello@chatwithpdf.ai"
    ),
    password=os.getenv("CUSTOM_SMTP_SERVER_PWD"),
    secure=True
)

print("API_DOMAIN:", os.getenv("API_DOMAIN"))
print("WEBSITE:", os.getenv("WEBSITE_DOMAIN"))

def custom_emailverification_delivery(original_implementation):
    async def send_email_via_brevo(template_vars, user_context: Dict[str, Any]) -> None:

        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")
        api_client = sib_api_v3_sdk.ApiClient(configuration)
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(api_client)
        
        # Define the email content
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": template_vars.user.email}],
            template_id=5,
            params={
                "verify_link": template_vars.email_verify_link  
            },
        )
        
        try:
            print(f"link is:{template_vars.email_verify_link}")
            api_response = api_instance.send_transac_email(send_smtp_email)
            print(f"Email sent successfully: {api_response}")
        except ApiException as e:
            print(f"Exception when calling TransactionalEmailsApi->send_transac_email: {e}")

    original_implementation.send_email = send_email_via_brevo
    return original_implementation

def custom_resetpassword_delivery(original_implementation):
    async def send_email_via_brevo(template_vars, user_context: Dict[str, Any]) -> None:
        
        configuration = Configuration()
        configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")   
        api_client = ApiClient(configuration)
        api_instance = TransactionalEmailsApi(api_client)

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": template_vars.user.email}],
            template_id=6,
            params={
                "verify_link": template_vars.password_reset_link  # Your dynamic verification link
            },
        )
        
        try:
            api_response = api_instance.send_transac_email(send_smtp_email)
            print(f"Password reset email sent successfully: {api_response}")
        except ApiException as e:
            print(f"Exception when calling TransactionalEmailsApi->send_transac_email: {e}")

    original_implementation.send_email = send_email_via_brevo
    return original_implementation

def override_thirdpartyemailpassword_functions(original_implementation: RecipeInterface) -> RecipeInterface:
    original_thirdparty_sign_in_up = original_implementation.thirdparty_sign_in_up
    original_emailpassword_sign_up = original_implementation.emailpassword_sign_up
    original_emailpassword_sign_in = original_implementation.emailpassword_sign_in

    async def emailpassword_sign_up(
        email: str,
        password: str,
        tenant_id: str,
        user_context: Dict[str, Any]
    ):
        # TODO: some pre sign up logic
        result = await original_emailpassword_sign_up(email, password, tenant_id, user_context)

        if isinstance(result, EmailPasswordSignUpOkResult):
            # TODO: some post sign up logic
            pass

        return result

    async def emailpassword_sign_in(
        email: str,
        password: str,
        tenant_id: str,
        user_context: Dict[str, Any]
    ):
        
        # TODO: some pre sign in logic
        result = await original_emailpassword_sign_in(email, password, tenant_id, user_context)

        if isinstance(result, EmailPasswordSignInOkResult):
            # TODO: some post sign in logic
            pass

        return result

    async def thirdparty_sign_in_up(
        third_party_id: str,
        third_party_user_id: str,
        email: str,
        oauth_tokens: Dict[str, Any],
        raw_user_info_from_provider: RawUserInfoFromProvider,
        tenant_id: str,
        user_context: Dict[str, Any]
    ):
        result = await original_thirdparty_sign_in_up(third_party_id, third_party_user_id, email, oauth_tokens, raw_user_info_from_provider, tenant_id, user_context)

        user = result.user
       
        
        user_info = result.raw_user_info_from_provider
        
        #Popup SignIn SignUp
        if hasattr(user_info, 'from_user_info_api') and user_info.from_user_info_api:
            raw_data = user_info.from_user_info_api

        #Single Click SignIn SignUp
        elif hasattr(user_info, 'from_id_token_payload') and user_info.from_id_token_payload:
            raw_data = user_info.from_id_token_payload
        
        print(f'raw data:{raw_data}')
       
        if result.created_new_user:
            try:
                user_id = user.user_id
                await update_user_metadata(user_id, {"email":raw_data.get("email"),"firstname": raw_data.get("given_name"),"lastname":raw_data.get("family_name")})
            except Exception as e:
                print(f"Error occurred: {str(e)}")
            print("New user was created")

        else:
            try:
                user_id = user.user_id
                is_user_id_present = UserMetaDataQueries.get_meta_data_details(user_id)
                if is_user_id_present == False:
                    await update_user_metadata(user_id, {"email":raw_data.get("email"),"firstname": raw_data.get("given_name"),"lastname":raw_data.get("family_name")})
                else:
                    print("User already existed and was signed in")
            except Exception as e:
                print(f"Error occurred: {str(e)}")
            # TODO: Post sign in logic
        
        return result

    original_implementation.emailpassword_sign_up = emailpassword_sign_up
    original_implementation.emailpassword_sign_in = emailpassword_sign_in
    original_implementation.thirdparty_sign_in_up = thirdparty_sign_in_up

    return original_implementation

init(
    app_info=InputAppInfo(
        app_name="ChatWithPDF",
        api_domain=os.getenv("API_DOMAIN"),
        website_domain=os.getenv("WEBSITE_DOMAIN"),
        api_base_path="/auth",
        website_base_path="/auth"
    ),
    supertokens_config=SupertokensConfig(
        connection_uri="http://localhost:3567",
    ),
    framework='django',
    recipe_list=[
        emailverification.init(
            mode='OPTIONAL',
            email_delivery=EmailDeliveryConfig(override=custom_emailverification_delivery)
        ),
        emailpassword.init(
            email_delivery=EmailDeliveryConfig(override=custom_resetpassword_delivery)
        ),
        session.init(), 
        thirdpartyemailpassword.init(
            override=thirdpartyemailpassword.InputOverrideConfig(
                functions=override_thirdpartyemailpassword_functions
            ),
            providers=[
                ProviderInput(
                    config=ProviderConfig(
                        third_party_id="google",
                        clients=[
                            ProviderClientConfig(
                                client_id=os.getenv('GOOGLE_CLIENT_ID'),
                                client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
                                scope=["https://www.googleapis.com/auth/userinfo.email","https://www.googleapis.com/auth/userinfo.profile"]
                            ),
                        ],
                    ),
                ),
            ]
        ),
        dashboard.init(),
        usermetadata.init()
    ],
    mode='asgi' 
)