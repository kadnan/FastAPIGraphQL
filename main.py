import graphene
from fastapi import FastAPI
from starlette.graphql import GraphQLApp

from models.contact import list_contacts, get_contact, create_contact


class Contact(graphene.ObjectType):
    first_name = graphene.String()
    last_name = graphene.String()
    email = graphene.String()


class QueryContact(graphene.ObjectType):
    contacts = graphene.List(Contact, id=graphene.Int())

    @staticmethod
    def resolve_contacts(self, info, id=0):
        records = []
        result = None

        if id == 0:
            contacts = list_contacts()
            for c in contacts:
                records.append({'first_name': c.first_name, 'last_name': c.last_name, 'email': c.email})
            result = records
        elif id > 0:
            contact = get_contact(id)
            if contact is not None:
                result = [{'first_name': contact.first_name, 'last_name': contact.last_name, 'email': contact.email}]
            else:
                result = []
        return result


class CreateContact(graphene.Mutation):
    # These fields will be displayed after successful insert
    id = graphene.Int()
    first_name = graphene.String()

    class Arguments:
        first_name = graphene.String()
        last_name = graphene.String()
        email = graphene.String()
        phone = graphene.String()

    def mutate(self, info, first_name, last_name, email, phone):
        new_contact = create_contact(first_name=first_name, last_name=last_name, email=email, phone=phone, status=1)

        if new_contact is None:
            raise Exception('Contact with the given email already exists')

        return CreateContact(id=new_contact.id, first_name=new_contact.first_name)


class Mutation(graphene.ObjectType):
    create_contact = CreateContact.Field()


app = FastAPI(title='ContactQL', description='GraphQL Contact APIs', version='0.1')


@app.get("/")
async def root():
    return {"message": "Contact Applications!"}


app.add_route("/graphql", GraphQLApp(graphiql=True, schema=graphene.Schema(query=QueryContact, mutation=Mutation)))
