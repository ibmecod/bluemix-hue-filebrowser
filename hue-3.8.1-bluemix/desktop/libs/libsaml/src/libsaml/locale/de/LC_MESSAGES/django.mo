��          �               <  Q   =  .   �  V   �       �   5  F   �  G   �  {   F  (   �     �  *     (   2  y   [  5   �  O     �   [  G     |  _  Q   �  3   .  r   b  -   �  �   	  h   �	  ]   
  �   i
  9   �
  &   1  )   X  6   �  �   �  F   T  h   �  �     _   �   A mapping from attributes in the response from the IdP to django user attributes. Allow responses that are initiated by the IdP. Attribute map directory contains files that map SAML attributes to pysaml2 attributes. Create users from IdP on login. Entity ID for Hue acting as service provider. Can also accept a pattern where '<base_url>' will be replaced with server URL base. Have Hue initiated authn requests be signed and provide a certificate. Have Hue initiated logout requests be signed and provide a certificate. IdP metadata in the form of a file. This is generally an XML file containing metadata that the Identity Provider generates. Optional attributes to ask for from IdP. Performs the logout or not. Request this NameID format from the server Required attributes to ask for from IdP. This is the public part of the service private/public key pair. cert_file must be a PEM formatted certificate chain file. Username can be sourced from 'attributes' or 'nameid' Xmlsec1 binary path. This program should be executable by the user running Hue. key_file is the name of a PEM formatted file that contains the private key of the Hue service. This is presently used both to encrypt/sign assertions and as client key in a HTTPS session. username_source not configured properly. SAML integration may not work. Project-Id-Version: Hue VERSION
Report-Msgid-Bugs-To: EMAIL@ADDRESS
POT-Creation-Date: 2015-07-19 15:13-0700
PO-Revision-Date: 2012-11-07 13:08-0800
Last-Translator: FULL NAME <EMAIL@ADDRESS>
Language-Team: de <LL@li.org>
Plural-Forms: nplurals=2; plural=(n != 1)
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit
Generated-By: Babel 0.9.6
 Eine Zuordnung von Attributen in der Antwort von IdP an Django-Benutzerattribute. Antworten zulassen, die durch IdP initiiert werden. Attributzuordnungsverzeichnis enthält Dateien, durch die SAML-Attribute den pysaml2-Attributen zugeordnet werden. Benutzer bei der Anmeldung aus IdP erstellen. Entitäts-ID für Hue fungiert als Dienstanbieter. Es kann auch ein Muster akzeptiert werden, dessen "<base_url>" durch die Server-URL-Datenbank ersetzt wird. Lassen Sie von Hue initiierte Authentifizierungsanforderungen signieren und geben Sie ein Zertifikat an. Lassen Sie von Hue initiierte Abmeldeanforderungen signieren und geben Sie ein Zertifikat an. IdP-Metadaten in Form einer Datei. Dies ist normalerweise eine XML-Datei, die Metadaten enthält, die vom Identity Provider generiert werden. Optionale Attribute, die von IdP abgerufen werden sollen. Führt die Anmeldung durch oder nicht. Dieses NameID-Format vom Server anfordern Erforderliche Attribute, die bei IdP abgefragt werden. Dies ist der öffentliche Teil des Schlüsselpaars für private/öffentliche Verwendung. "cert_file" muss eine PEM-formatierte Zertifikatkettendatei sein. Der Benutzername kann aus "attributes" oder "nameid" entnommen werden. Xmlsec1-Binärpfad. Dieses Programm sollte von dem Benutzer verwendet werden können, der Hue ausführt. "key_file" ist der Name einer PEM-formatierten Datei, die den privaten Schlüssel des Hue-Dienstes enthält. Dieser wird derzeit zum Verschlüsseln/Signieren von Bestätigungen und als Client-Schlüssel in einer HTTPS-Sitzung verwendet. username_source ist nicht korrekt konfiguriert. SAML-Integration ist vielleicht nicht möglich. 