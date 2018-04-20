function disenableMyProfile(form) 
	{
		
		var Form = document.getElementById(form);
		if(document.getElementById("buton").value == "Edytuj")
		{
            	for(I = 0; I < Form.length; I++) 
		 {
   		 		Form[I].disabled =false;
				
	         }
		document.getElementById("buton").value = "Zapisz";
		return;
         	}
		if(document.getElementById("buton").value == "Zapisz")
		{
            	for(I = 0; I < Form.length; I++) 
		 {
   		 		Form[I].disabled =true;
	         }
		document.getElementById("buton").value = "Edytuj";
		return;
         	}
	}

function disenableDevUs(form) 
	{
		
		var Form = document.getElementById(form);
		if(Form[Form.length-1].value == "Edytuj")
		{
			for(I=0;I<Form.length-1;I++)
			{
				Form[I].disabled =false;
			}
			Form[Form.length-1].value="Zapisz";
		}
		else
		{
			for(I=0;I<Form.length-1;I++)
			{
				Form[I].disabled =true;
			}
			Form[Form.length-1].value="Edytuj";
		}
	}
