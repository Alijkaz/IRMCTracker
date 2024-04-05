import { SlashCommandBuilder, EmbedBuilder } from 'discord.js';
import { getServer } from '../../services/serversService';
import { getServerEmbed } from '../../services/messagingService';


const command: TrackerCommand = {
	data: new SlashCommandBuilder()
		.setName('vote')
		.setDescription('💻 دریافت اطلاعات سرور مورد نظر')
		.addStringOption(option => option.setName('server').setDescription('اسم سرور').setRequired(true)),
	async execute(_, interaction) {
		const serverName: string = interaction.options.getString('server', true);

		await interaction.reply("🤔 چند لحظه صبر کن...");

		const server = await getServer(serverName);

		if (server == null) {
			return await interaction.reply({
				embeds: [
					new EmbedBuilder()
						.setColor("Red")
						.setTitle('🔴 سرور وارد شده وجود نداره!')
				]
			});
		}

		const embed = getServerEmbed(server);

		await interaction.editReply({ embeds: [embed] });
	},

};

export default command
