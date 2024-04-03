import { StyleSheet, Text, TextInput, View } from 'react-native';
import React, {useState, useEffect} from 'react';

const DashBoard = ( {navigation, route}) => {
    const {leagueID} = route.params;


    useEffect( () => {
        async function apiRequest(){
            const response = await fetch('http://localhost:5000', {
                method : "GET",
                headers : {
                    "Access-Control-Allow-Origin" : "*"
                }
            })
            const token = await response.json()
            console.log(token)
        }

        apiRequest()
    })


    return (
         <Text>Dash Board {JSON.stringify(leagueID)}</Text>
    )
}
export default DashBoard
